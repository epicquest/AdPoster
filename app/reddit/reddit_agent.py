import ast
import os
from datetime import datetime

import praw
import json
import time
from typing import List, Dict, Optional, Union
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseOutputParser
from langchain.prompts import PromptTemplate
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field

class RedditSearchInput(BaseModel):
    """Input for the Reddit community searcher tool."""
    keywords: List[str] = Field(..., description="A list of keywords to search for.")


class RedditCommunityTool(BaseTool):
    """Tool for searching Reddit communities and extracting posting rules"""
    name: str = "reddit_community_searcher"
    description: str = "Searches for Reddit communities related to keywords and extracts posting rules. Input should be a list of strings or a comma-separated string of keywords."
    reddit: Optional[object] = Field(default=None, exclude=True)
    parent_agent: object = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT", "CommunityResearcher/1.0")
            )
        except Exception as e:
            print(f"Warning: Could not initialize Reddit client: {e}")
            self.reddit = None

    def _run(self, keywords: Union[List[str], str]) -> str:
        """Search for relevant subreddits and return formatted results"""
        if self.reddit is None:
            return "Error: Reddit client not initialized. Please check your Reddit API credentials."

        # Handle the input type
        if isinstance(keywords, str):
            try:
                # Safely convert the string representation of a list back to a list
                keywords_list = ast.literal_eval(keywords)
                if not isinstance(keywords_list, list):
                    raise ValueError("Input string is not a valid list.")
                keywords = keywords_list
            except (ValueError, SyntaxError):
                # If it's not a list, try to split it by commas
                keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        # else:
        #      return f"Error: Invalid input type for keywords: {type(keywords)}. Expected a list or string."

        try:
            results = self.search_communities(keywords)

            # This is the key change: save the results to the parent agent's state
            self.parent_agent.community_data = results

            # Return a simple, easy-to-parse string for the LLM
            community_names = [c['name'] for c in results]
            if community_names:
                return f"Found {len(results)} communities. The top ones are: {', '.join(community_names[:5])}. The data has been stored for analysis."
            else:
                return "No relevant communities were found."

        except Exception as e:
            return f"Error searching communities: {str(e)}"

    def search_communities(self, keywords: List[str]) -> List[Dict]:
        """Search for relevant subreddits based on keywords"""

       # keywords = self.extract_keywords(app_description)

        communities = []

        # Search for each keyword
        for keyword in keywords:
            try:
                # Search subreddits
                subreddits = self.reddit.subreddits.search(keyword, limit=5)

                for subreddit in subreddits:
                    if subreddit.subscribers is not None and subreddit.subscribers > 1000:  # Filter small communities
                        community_info = self.get_community_info(subreddit)
                        if community_info:
                            communities.append(community_info)

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"Error searching for keyword '{keyword}': {e}")
                continue

        # Remove duplicates and sort by relevance
        unique_communities = self.deduplicate_communities(communities)
        return sorted(unique_communities, key=lambda x: x['subscribers'], reverse=True)

    def get_community_info(self, subreddit) -> Optional[Dict]:
        """Get detailed information about a subreddit including rules"""
        try:
            # Get basic info
            community_info = {
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.public_description,
                'subscribers': subreddit.subscribers,
                'url': f"https://reddit.com/r/{subreddit.display_name}",
                'created_utc': subreddit.created_utc,
                'over_18': subreddit.over18,
                'rules': [],
                'sidebar_rules': []
            }

            # Get subreddit-specific rules
            try:
                rules = subreddit.rules()
                for rule in rules:
                    # Handle both rule objects and strings
                    if hasattr(rule, 'short_name'):
                        # It's a rule object
                        rule_info = {
                            'short_name': rule.short_name,
                            'description': getattr(rule, 'description', ''),
                            'kind': getattr(rule, 'kind', ''),
                            'priority': getattr(rule, 'priority', 0),
                            'violation_reason': getattr(rule, 'violation_reason', None)
                        }
                    elif isinstance(rule, str):
                        # It's just a string
                        rule_info = {
                            'short_name': rule,
                            'description': rule,
                            'kind': 'text',
                            'priority': 0,
                            'violation_reason': None
                        }
                    else:
                        # Try to extract what we can
                        rule_info = {
                            'short_name': str(rule),
                            'description': str(rule),
                            'kind': 'unknown',
                            'priority': 0,
                            'violation_reason': None
                        }

                    community_info['rules'].append(rule_info)

            except Exception as e:
                print(f"Could not fetch subreddit rules for r/{subreddit.display_name}: {e}")

            # Get sidebar content and extract rules from it
            try:
                if subreddit.description:
                    # Extract rules from sidebar description
                    sidebar_rules = self.extract_rules_from_sidebar(subreddit.description)
                    community_info['sidebar_rules'] = sidebar_rules

                    # If no formal rules found, use sidebar as primary source
                    if not community_info['rules'] and sidebar_rules:
                        for sidebar_rule in sidebar_rules[:5]:  # Top 5 sidebar rules
                            rule_info = {
                                'short_name': sidebar_rule[:50] + "..." if len(sidebar_rule) > 50 else sidebar_rule,
                                'description': sidebar_rule,
                                'kind': 'sidebar',
                                'priority': 0,
                                'violation_reason': None
                            }
                            community_info['rules'].append(rule_info)
                else:
                    community_info['sidebar_rules'] = []

            except Exception as e:
                print(f"Could not fetch sidebar for r/{subreddit.display_name}: {e}")
                community_info['sidebar_rules'] = []

            # Try to get some common Reddit posting requirements
            community_info['common_requirements'] = self.get_common_posting_requirements()

            return community_info

        except Exception as e:
            print(f"Error getting info for subreddit: {e}")
            return None

    def get_common_posting_requirements(self) -> List[str]:
        """Return common Reddit posting requirements that apply to most subreddits"""
        return [
            "Follow Reddit's Content Policy",
            "No spam or excessive self-promotion",
            "Be respectful and civil in discussions",
            "No personal information or doxxing",
            "Follow the 9:1 rule (90% community participation, 10% self-promotion)",
            "Read and follow subreddit-specific rules",
            "Use appropriate flair when required",
            "Search before posting to avoid duplicates"
        ]

    def extract_posting_guidelines(self, site_rules_flow: List[Dict]) -> List[str]:
        """Extract meaningful posting guidelines from the complex site_rules_flow structure"""
        guidelines = []

        for rule_flow in site_rules_flow:
            if 'reasonTextToShow' in rule_flow and rule_flow['reasonTextToShow']:
                # Clean up the text (remove concatenated words)
                text = rule_flow['reasonTextToShow']
                # Add spaces before capital letters that follow lowercase letters
                import re
                text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
                guidelines.append(text)

            # Recursively extract from nested reasons
            if 'nextStepReasons' in rule_flow:
                nested_guidelines = self.extract_posting_guidelines(rule_flow['nextStepReasons'])
                guidelines.extend(nested_guidelines)

        # Remove duplicates and return most relevant ones
        unique_guidelines = list(set(guidelines))
        return unique_guidelines[:10]  # Limit to top 10 most relevant

    def extract_rules_from_sidebar(self, sidebar_text: str) -> List[str]:
        """Extract rules from sidebar markdown text"""
        import re

        # Look for common rule patterns
        rule_patterns = [
            r'(?i)rule\s*\d+[:\-\.]?\s*([^\n\r]+)',
            r'(?i)^\d+\.\s*([^\n\r]+)',
            r'(?i)^\*\s*([^\n\r]+)',
            r'(?i)^-\s*([^\n\r]+)'
        ]

        rules = []
        for pattern in rule_patterns:
            matches = re.findall(pattern, sidebar_text, re.MULTILINE)
            rules.extend(matches)

        # Clean up rules
        cleaned_rules = []
        for rule in rules:
            rule = rule.strip()
            if len(rule) > 10 and len(rule) < 200:  # Filter reasonable length rules
                cleaned_rules.append(rule)

        return cleaned_rules[:10]  # Return top 10 rules

    def deduplicate_communities(self, communities: List[Dict]) -> List[Dict]:
        """Remove duplicate communities"""
        seen = set()
        unique = []
        for community in communities:
            if community['name'] not in seen:
                seen.add(community['name'])
                unique.append(community)
        return unique


class CommunityAnalysisTool(BaseTool):
    """Tool for analyzing communities and determining relevance"""

    name: str = "community_analyzer"
    description: str = "Analyzes Reddit communities to determine relevance for app promotion and summarizes posting requirements"
    parent_agent: object = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)

    def _run(self, query: str) -> str:
        """Analyze community data and provide insights"""
        communities = self.parent_agent.community_data

        if not communities:
            return "No community data is available for analysis. Please run the `reddit_community_searcher` tool first."

        try:
            analysis = self.analyze_communities(communities)
            return json.dumps(analysis, indent=2)
        except Exception as e:
            return f"Error analyzing communities: {str(e)}"

    def analyze_communities(self, communities: List[Dict]) -> Dict:
        """Analyze communities and provide recommendations"""
        analysis = {
            'total_communities': len(communities),
            'high_potential': [],
            'medium_potential': [],
            'low_potential': [],
            'summary': {}
        }

        for community in communities:
            score = self.calculate_relevance_score(community)
            community['relevance_score'] = score

            if score >= 8:
                analysis['high_potential'].append(community)
            elif score >= 5:
                analysis['medium_potential'].append(community)
            else:
                analysis['low_potential'].append(community)

        # Generate summary
        analysis['summary'] = {
            'recommended_communities': len(analysis['high_potential']),
            'total_subscribers': sum(c['subscribers'] for c in analysis['high_potential']),
            'common_rules': self.extract_common_rules(communities)
        }

        return analysis

    def calculate_relevance_score(self, community: Dict) -> int:
        """Calculate relevance score (1-10) for a community"""
        score = 5  # Base score

        # Subscriber count factor
        if community['subscribers'] > 100000:
            score += 2
        elif community['subscribers'] > 10000:
            score += 1

        # Rule complexity (fewer complex rules = higher score)
        if len(community['rules']) < 5:
            score += 1

        # Check for promotion-friendly indicators
        description_lower = (community['description'] or '').lower()
        title_lower = (community['title'] or '').lower()

        promotion_friendly = ['showcase', 'share', 'promote', 'feedback', 'review']
        if any(word in description_lower or word in title_lower for word in promotion_friendly):
            score += 2

        # Penalize if over 18
        if community['over_18']:
            score -= 2

        return max(1, min(10, score))

    def extract_common_rules(self, communities: List[Dict]) -> List[str]:
        """Extract common posting rules across communities"""
        rule_counts = {}

        for community in communities:
            # Count subreddit-specific rules
            for rule in community.get('rules', []):
                rule_key = rule.get('short_name', '').lower() if rule.get('short_name') else ''
                if rule_key and len(rule_key) > 2:
                    rule_counts[rule_key] = rule_counts.get(rule_key, 0) + 1

            # Count sidebar rules
            for sidebar_rule in community.get('sidebar_rules', []):
                if isinstance(sidebar_rule, str) and len(sidebar_rule) > 5:
                    # Simple keyword extraction
                    sidebar_lower = sidebar_rule.lower()
                    if 'promotion' in sidebar_lower or 'advertising' in sidebar_lower:
                        rule_counts['promotion restrictions'] = rule_counts.get('promotion restrictions', 0) + 1
                    if 'spam' in sidebar_lower:
                        rule_counts['no spam'] = rule_counts.get('no spam', 0) + 1
                    if 'quality' in sidebar_lower:
                        rule_counts['quality content'] = rule_counts.get('quality content', 0) + 1
                    if 'self-promotion' in sidebar_lower or 'self promotion' in sidebar_lower:
                        rule_counts['self-promotion rules'] = rule_counts.get('self-promotion rules', 0) + 1
                    if 'flair' in sidebar_lower:
                        rule_counts['flair required'] = rule_counts.get('flair required', 0) + 1

        # Get most common rules
        common_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return [rule[0] for rule in common_rules if rule[1] >= 1]  # All rules that appear


class RedditCommunityAgent:
    """Main agent class for Reddit community research"""

    def __init__(self, google_api_key: str, model_name: str = "gemini-1.5-flash"):
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=google_api_key,
            model=model_name,
            temperature=0.1
        )
        self.community_data = []

        # Initialize tools
        self.tools = [
            RedditCommunityTool(parent_agent=self),  # Pass a reference to self
            CommunityAnalysisTool(parent_agent=self)
        ]

        # Initialize agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def research_communities(self, app_description: str, keywords: list[str]) -> Dict:
        """Main method to research communities for an app"""

        # Define a JSON-like string of the keywords to embed in the prompt
        # This makes it very clear to the LLM what the list looks like
        keywords_json = json.dumps(keywords)

        prompt = f"""
        You are a marketing analyst for an app. I have provided you with a description of the app and a pre-extracted list of keywords related to it.

        App Description: "{app_description}"
        Pre-extracted Keywords: {keywords_json}

        Your primary task is to find and analyze relevant Reddit communities. You have two tools at your disposal: `reddit_community_searcher` and `community_analyzer`.

        Follow these steps in order:
        1.  Call the `reddit_community_searcher` tool. **The input to this tool must be the literal list of keywords I have provided.**
        2.  Once you have the community data, call the `community_analyzer` tool with that data to get an analysis.
        3.  Finally, summarize your findings to answer the user's request, including recommended communities, key posting rules, and best practices.
        """

        try:
            result = self.agent.run(prompt)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

def main():
    """Example usage of the Reddit Community Agent"""

    # Set up environment variables
    # You'll need to set these:
    # REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, GOOGLE_API_KEY

    # Check if required environment variables are set
    required_env_vars = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "GOOGLE_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set these environment variables:")
        print("export REDDIT_CLIENT_ID='your_client_id'")
        print("export REDDIT_CLIENT_SECRET='your_client_secret'")
        print("export REDDIT_USER_AGENT='YourApp/1.0'")
        print("export GOOGLE_API_KEY='your_google_api_key'")
        return

    # Initialize agent
    agent = RedditCommunityAgent(google_api_key=os.getenv("GOOGLE_API_KEY"))

    # Example app description
    # app_description = """
    # Blast off into Terra Nova, the funniest space adventure on Android! 🌌
    # Your choices matter! Mine asteroids, explore planets, and trade your way to
    # galactic domination. 😉\n\n🌟 **Why You'll Love Terra Nova:**\n\n*
    # **Choose Your Path:** Every decision shapes your destiny!
    # Build your empire, mine valuable resources or trade with aliens. \n*
    # **Hilarious Descriptions:** Get ready to chuckle at witty and ironic descriptions,
    #  making every moment entertaining.\n*   **Unique Spaceships & Modules:**
    #  Upgrade and customize your fleet with quirky personalities. 🚀\n*
    #   **Pop Culture References:** Spot countless references to your favorite movies, shows, and books! 👀\n
    #   *   **Strategic Gameplay:** Plan your moves, outsmart your rivals, and become the ultimate space tycoon!\n\n✅ **Completely Free to Play! Powered by Gemini AI. No in-app purchases! Original Gameplay!**\n\nD
    #   Download Terra Nova now and embark on a hilarious space adventure! Ready to shape your galactic destiny? 🌠",
    #
    # """
    app_description = "Blast off into Terra Nova, the funniest space adventure on Android! 🌌 Your choices matter! Mine asteroids, explore planets, and trade your way to galactic domination. 😉\n\n🌟 **Why You'll Love Terra Nova:**\n\n*   **Choose Your Path:** Every decision shapes your destiny! Build your empire, mine valuable resources or trade with aliens. \n*   **Hilarious Descriptions:** Get ready to chuckle at witty and ironic descriptions, making every moment entertaining.\n*   **Unique Spaceships & Modules:** Upgrade and customize your fleet with quirky personalities. 🚀\n*   **Pop Culture References:** Spot countless references to your favorite movies, shows, and books! 👀\n*   **Strategic Gameplay:** Plan your moves, outsmart your rivals, and become the ultimate space tycoon!\n\n✅ **Completely Free to Play! Powered by Gemini AI. No in-app purchases! Original Gameplay!**\n\nDownload Terra Nova now and embark on a hilarious space adventure! Ready to shape your galactic destiny? 🌠"
    app_keywords: list[str] = ["TerraNova",
      "AndroidGames",
      "SpaceAdventure",
      "SciFi",
      "MobileGaming",
      "FreeGames",
      "Galaxy",
      "Spaceships",
      "FunnyGames",
      "GameDev",
      "IndieGame",
      "StrategyGame",
      "NoAds",
      "NoInAppPurchases",
      "GeminiAI",
      "Gaming",
      "Gamer",
      "Games",
      "VideoGames",
      "Fun",
      "Entertainment",
      "EpicQuestStudios",
      "ChooseYourOwnAdventure",
      "SpaceOpera",
      "PopCulture",
      "AndroidApp",
      "NewGame",
      "MustPlay",
      "DownloadNow",
      "GamerLife"]

    # app_keywords: list[str] = ["AndroidGames",
    #                            "SpaceAdventure"]
    print("Starting Reddit community research...")
    result = agent.research_communities(app_description, app_keywords)

    if result["status"] == "success":
        print("Research completed successfully!")
        print(result["result"])
    else:
        print(f"Error occurred: {result['error']}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"reddit_research_results_{timestamp}.json"
    with open(output_filename, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nResearch results have been saved to '{output_filename}'")

if __name__ == "__main__":
    main()