"""
Configuration file for AdPoster
Copy this to config.py and fill in your actual values
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# App Templates - You can define multiple apps here
APP_TEMPLATES = {
    # "fitness_app": {
    #     "name": "FitnessTracker Pro",
    #     "description": "Complete fitness tracking app with workout plans, nutrition tracking, and progress analytics",
    #     "category": "Health & Fitness",
    #     "key_features": [
    #         "Custom workout plans",
    #         "Calorie tracking",
    #         "Progress analytics",
    #         "Social sharing",
    #         "Offline mode"
    #     ],
    #     "target_audience": "Fitness enthusiasts aged 18-45",
    #     "play_store_url": "https://play.google.com/store/apps/details?id=com.example.fitnesstracker"
    # },
    #
    # "productivity_app": {
    #     "name": "TaskMaster",
    #     "description": "Smart task management app with AI-powered scheduling and productivity insights",
    #     "category": "Productivity",
    #     "key_features": [
    #         "AI task scheduling",
    #         "Team collaboration",
    #         "Time tracking",
    #         "Goal setting",
    #         "Cross-platform sync"
    #     ],
    #     "target_audience": "Professionals and students aged 22-50",
    #     "play_store_url": "https://play.google.com/store/apps/details?id=com.example.taskmaster"
    # },

    "game_terra_nova": {
        "name": "Terra Nova",
        "description": """Choices, Spaceships & Pop Culture Shenanigans! 🚀🪐

Welcome to 🌌Terra Nova, the funniest and most entertaining space adventure on Android! In this galaxy, your choices matter – whether you're mining precious resources, scanning mysterious planets, or trading in the intergalactic market, every decision you make will shape your journey. 🚀🪐

🌟 Key Features:

Choose Your Path: From mining asteroids to building the ultimate spaceship, every action has a consequence.
Hilarious Descriptions: Enjoy witty and ironic descriptions that will make you chuckle as you explore the universe.
Unique Modules & Spaceships: Unlock and upgrade a variety of spaceships and modules, each with their own quirky personality.
Pop Culture References: Spot countless references to your favorite movies, shows, and books hidden throughout the game.
Strategic Gameplay: Plan your moves carefully to become the ultimate space tycoon!

Ready to embark on a hilarious space adventure? Download Terra Nova now and start shaping your galactic destiny, one funny decision at a time!""",
        "category": "Text-based games",
        "key_features": [
            "Add free",
            "Powered by Gemini AI",
            "No in-app purchases",
            "Original gameplay",
            "Deep game-mechanics"
        ],
        "game_guide": """
                Terra Nova is a text- and puzzle-based adventure where you complete quests by performing actions. Each action carries a chance of success. When you succeed, you earn rewards; when you fail, you may lose resources. Your ultimate goal is to progress through quests, upgrade your ships and base, and eventually construct the Celestial Gate.

Gameplay Overview

You begin on your home planet with your starter ship:
🛸 Noob Spacecraft – Into The Maybe
At the start, you’ll see:
Quests → Your main objectives with requirements and rewards.
Actions → The moves you can perform to progress quests.
Quests
Quests are story-driven goals.
Each quest lists what you need to do and what you’ll earn.
Example: The Miner’s Trial – harvest a mineral from an asteroid field. Reward: +1 mineral.
Actions
Every action has three parts:
Requirements (left side) → Resources consumed to perform the action.
Success Chance (top right) → Probability of success (depends on game difficulty).
Reward (right side) → Resources gained on success.

Starting the Game

Choose a Difficulty
Perform Your First Action

Action: Mining
Requirement: none
Success Chance: 95%
Reward: +1 mineral
Check the Result

✅ Green check screen → success (rewards shown)
❌ Red fail screen → failure (often with fun pop-culture jokes)

Complete Your First Quest

On success, you finish The Miner’s Trial and gain your reward.

Game Systems
Spaceport

Accessed via the bottom-right button (next to Home).
Manage your active spaceship, which determines available actions and action results.

New ships can be acquired:
As quest rewards
Purchased at planets with ship shops (revealed after scanning).

Spaceships
Each spaceship has:
Name (AI-generated, usually pop-culture inspired)
Type (e.g., MINER, SCANNER, TRANSPORTER, VENDOR_VESSEL, ACQUISITION_CRUISER, CONSTRUCTION_BARGE, NOOBIE_SHIP)
Stats:
Module slots (by type)
Mining / Scanning strength (affects results)
Cargo capacity (max material storage during missions)
Cost (if buyable)
Traits (special bonuses)

Note: Noobie Ship cannot be sold.

Modules

Found in the Modules tab (bottom-right button).
Earned through quests or purchased at module shops (after scanning planets).
Two categories:
Spaceship Modules – scanUpgrades, transportUpgrades, miningUpgrades, utilities
HQ Base Modules – economyUpgrades, buildingUpgrades, craftingUpgrades
HQ slots can be expanded by building upgrades.

Progression & Quests

Quest 1: The Miner’s Trial

Action: Mining

Reward: +1 mineral

Quest 2: Planet Scouting

Action: Scanning

Unlocks mining on Planet 2

Quest 3: Build Material Storage

Requirement: 3 minerals

Action: Build Material Storage (randomly appears if requirements met)

Reward: Storage capacity increases from 5 → 10

🔹 Storage is accessed via the bottom-left icon (shows capacity).

Quest 4: Build Market

Requirement: 5 minerals

...

Final Quest: Build the Celestial Gate on the last planet.

Interface Quick Reference

Bottom Middle Button → Home screen (HQ buildings overview)

Bottom Left Button → Quest list (current objectives & requirements)

Bottom Right Buttons →

Spaceport (manage ships)

Modules tab (install HQ/ship upgrades)

Planets (view planets + available actions after scanning)

Winning the Game

The game ends when you complete the final quest by reaching the last planet and constructing the Celestial Gate.
""",
        "target_audience": "Gamers aged 13-60",
        "play_store_url": "https://play.google.com/store/apps/details?id=com.epicqueststudios.oneoffive"
    },


    "illusion_of_mastery": {
        "name": "Illusion of Mastery",
        "description": """Unleash Your True Potential with Illusion of Mastery!

Ever felt like you know something, only to freeze when tested? That's the "Illusion of Mastery." Our app helps you shatter that illusion by turning any keyword into a unique, challenging quiz. Confidence is cheap, knowledge isn't.

Just type a keyword, and instantly generate a custom quiz. It's the perfect way to expose what you truly know and where you need to grow.

Why Illusion of Mastery?

Banish the Illusion: Discover your real understanding, not just what you think you know.
Personalized Learning: Create quizzes on any topic, from "Quantum Physics" to "Classic Cocktails."
Active Recall: Proven to boost retention by actively retrieving information, not just rereading.
Engaging & Effective: Make learning fun and stay motivated.
Track Your Progress: See your scores and pinpoint areas for improvement.
How It Works:

Enter Keyword: Type your topic.
Generate Quiz: Get a custom quiz instantly.
Take Quiz: Challenge yourself!
Review & Learn: Get immediate feedback.

Perfect for students, lifelong learners, or anyone eager to truly master a subject. Don't let false confidence hold you back. Download Illusion of Mastery today and invest in real knowledge!""",
        "category": "Education",
        "key_features": [
            "Add free",
            "Powered by Gemini AI",
            "No in-app purchases",
            "Get feedback immediatelly"
        ],
        "game_guide": """
Enter Keyword
Type the topic you want to master.

Generate Quiz
Instantly get a custom quiz tailored to your keyword.

Take Quiz
Challenge yourself and see what you really know.

Review & Learn
Get immediate feedback to reinforce learning and fill knowledge gaps.
""",
        "target_audience": "People aged 13-60",
        "play_store_url": "https://play.google.com/store/apps/details?id=com.epicqueststudios.illusionofmasteryandroid"
    }
}

PLATFORM_SETTINGS = {
    "facebook": {
        "max_chars": 2200,
        "hashtag_limit": 30,
        "optimal_image_size": (1200, 630),
        "aspect_ratio": "16:9",  # Closest to 1200x630
        "tone": "friendly and engaging",
        "style": "clean, vibrant visuals with clear subjects, community-oriented feel",
        "best_practices": [
            "Use short paragraphs and emojis to boost engagement.",
            "Images with people perform better than generic graphics.",
            "Aim for community-focused messaging."
        ]
    },
    "instagram": {
        "max_chars": 2200,
        "hashtag_limit": 30,
        "optimal_image_size": (1080, 1080),
        "aspect_ratio": "1:1",  # Square format
        "tone": "visual and trendy",
        "style": "aesthetic, modern, bold colors, eye-catching composition",
        "best_practices": [
            "Use carousels for higher engagement.",
            "Leverage Stories/Reels for reach.",
            "Keep captions short; let visuals do the talking."
        ]
    },
    "twitter": {
        "max_chars": 280,
        "hashtag_limit": 10,
        "optimal_image_size": (1200, 675),
        "aspect_ratio": "16:9",  # Closest to 1200x675
        "tone": "concise and punchy",
        "style": "minimalistic, high contrast, quick-to-digest imagery",
        "best_practices": [
            "Keep text short and impactful.",
            "Use 1–2 hashtags max for relevance.",
            "Threads work well for storytelling."
        ]
    },
    "linkedin": {
        "max_chars": 3000,
        "hashtag_limit": 20,
        "optimal_image_size": (1200, 627),
        "aspect_ratio": "16:9",  # Closest to 1200x627
        "tone": "professional and informative",
        "style": "corporate, trustworthy, clear visuals with a polished look",
        "best_practices": [
            "Use professional and educational tone.",
            "Include data-driven insights or case studies.",
            "Native documents and carousels drive more reach."
        ]
    },
    "tiktok": {
        "max_chars": 2200,
        "hashtag_limit": 20,
        "optimal_image_size": (1080, 1920),
        "aspect_ratio": "9:16",  # Vertical video format
        "tone": "fun and energetic",
        "style": "dynamic, colorful, high-energy, visually playful",
        "best_practices": [
            "Hook viewers in first 3 seconds.",
            "Use trending sounds and effects.",
            "Keep videos between 10–30 seconds."
        ]
    },
    "bluesky": {
        "max_chars": 200,
        "hashtag_limit": 5,  # Not enforced, hashtags uncommon
        "optimal_image_size": (1200, 675),
        "max_image_filesize_kb": 976,  # Hard limit from API
        "aspect_ratio": "16:9",
        "tone": "casual, authentic, and community-driven",
        "style": "clean, relatable visuals; organic feel; less polished, more 'real'",
        "best_practices": [
            "Keep text under 300 chars — short and conversational.",
            "Avoid heavy hashtag use; plain words are preferred.",
            "Images must be < 976 KB.",
            "Replying and engaging boosts visibility."
        ]
    }
}


# Output Settings
OUTPUT_DIRECTORY = "output"
LOG_LEVEL = "INFO"
SAVE_IMAGES = True
SAVE_JSON = True

# Image Generation Settings
IMAGE_SETTINGS = {
    "default_background_color": "#1a237e",
    "title_color": "#ffffff",
    "accent_color": "#ffc107",
    "cta_color": "#4caf50",
    "default_font_size_title": 48,
    "default_font_size_body": 32
}