import os
import re
import json

class TrekAIAssistant:
    """
    Intelligent Trekking Advisor & Chatbot with built-in domain NLP knowledge,
    custom packing list generation, day-by-day itinerary planning,
    and optional external LLM integration (Gemini / OpenAI).
    """

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def generate_packing_list(self, trek_name, duration=3, difficulty="Moderate"):
        """
        Generates a categorized, essential packing checklist tailored for the trek.
        """
        is_hard = difficulty.lower() == "hard"
        is_long = duration >= 5

        clothing = [
            "Quick-dry moisture-wicking trekking t-shirts (3-4 pairs)",
            "Trekking pants (convertible, lightweight and water-resistant)",
            "Warm thermal base layer (top & bottom) for nights",
            "Fleece jacket or warm pullover",
            "Puffer/Down jacket (rated for sub-zero temperatures)" if is_hard or is_long else "Windproof light fleece jacket",
            "Waterproof rain poncho or Gore-Tex jacket & rain pants",
            "3-4 pairs of quick-dry woolen & athletic trekking socks",
            "Warm woolen beanie and sun hat / cap",
            "Waterproof fleece-lined trekking gloves"
        ]

        footwear_gear = [
            "High-ankle waterproof trekking shoes with good grip (vibram sole recommended)",
            "Comfortable camp footwear / slip-ons for evening relaxation",
            "Adjustable trekking poles with shock absorption",
            "50-60L ergonomic backpack with rain cover" if is_long else "30-40L sturdy daypack with rain cover",
            "UV400 Category 3 sunglasses (essential to prevent snow blindness)"
        ]

        safety_medical = [
            "Personal First Aid Kit (bandages, antiseptic ointment, blister tape, crepe bandage)",
            "Essential medications: Paracetamol, Ibuprofen, ORS sachets, Antacid",
            "Diamox (acetazolamide) for Acute Mountain Sickness (consult doctor first)",
            "High-SPF sunscreen (SPF 50+) and hydrating lip balm",
            "Headlamp or LED flashlight with extra batteries",
            "Water purification tablets or LifeStraw filter bottle"
        ]

        essentials = [
            "2x Reusable 1-liter insulated water bottles or hydration bladder",
            "High-energy trail snacks (dry fruits, nuts, energy bars, dark chocolate)",
            "Biodegradable toiletries, wet wipes, and sanitizer",
            "Quick-dry microfiber towel",
            "Waterproof dry bags / zip-locks for phone, power bank, and cash",
            "Government-issued Photo ID card & trek permit copies"
        ]

        return {
            "trek_name": trek_name,
            "difficulty": difficulty,
            "duration": f"{duration} Days",
            "categories": {
                "Clothing & Layering": clothing,
                "Footwear & Trail Gear": footwear_gear,
                "Medical & Safety": safety_medical,
                "Hydration, Food & Documents": essentials
            }
        }

    def generate_itinerary(self, trek_name, location="Himalayas", duration=4, difficulty="Moderate"):
        """
        Generates a realistic day-wise expedition itinerary.
        """
        days = []
        dur = max(2, min(14, int(duration)))

        # Day 1: Basecamp Arrival
        days.append({
            "day": 1,
            "title": f"Arrival at Base Camp ({location})",
            "altitude": "Approx. 6,000 ft",
            "details": f"Arrive at the starting basecamp for {trek_name}. Meet certified trek leaders, gear inspection, safety briefing, and evening acclimatization walk."
        })

        # Trail days
        altitudes = [7800, 9500, 11200, 12500, 14100, 15500]
        for d in range(2, dur):
            alt_idx = min(len(altitudes) - 1, d - 2)
            alt_val = altitudes[alt_idx]
            if d == dur - 1:
                # Summit / High pass day
                days.append({
                    "day": d,
                    "title": f"Summit Push / High Trail to Ridge of {trek_name}",
                    "altitude": f"Approx. {alt_val + 1200} ft",
                    "details": "Early morning start (4:00 AM) for spectacular sunrise views over panoramic Himalayan peaks. Descend back to the high camp."
                })
            else:
                days.append({
                    "day": d,
                    "title": f"Ascent to Camp {d - 1} via scenic pine ridges and alpine meadows",
                    "altitude": f"Approx. {alt_val} ft",
                    "details": "Moderate gradient trek through dense oak and rhododendron forests. Gradual altitude gain with regular hydration stops."
                })

        # Final Day: Descent
        days.append({
            "day": dur,
            "title": "Descent to Base & Return Journey",
            "altitude": "Approx. 5,500 ft",
            "details": f"Morning descent following scenic river valleys back to basecamp. Certificate distribution, celebratory farewell, and departure."
        })

        return {
            "trek_name": trek_name,
            "duration": dur,
            "difficulty": difficulty,
            "days": days
        }

    def chat_response(self, user_msg, all_treks=None):
        """
        Answers user inquiries about trekking, routes, gear, preparation,
        and database treks using domain NLP and fallback to live LLM if configured.
        """
        msg = (user_msg or "").strip()
        msg_lower = msg.lower()

        # 1. Check for LLM API integration if configured
        if self.gemini_api_key or self.openai_api_key:
            llm_reply = self._call_llm_if_available(msg, all_treks)
            if llm_reply:
                return llm_reply

        # 2. Built-in Domain NLP Knowledge Engine
        # Query: Treks in specific location or matching criteria
        if any(w in msg_lower for w in ["recommend", "suggest", "which trek", "what trek", "options", "available"]):
            if all_treks:
                if "easy" in msg_lower or "beginner" in msg_lower:
                    matched = [t for t in all_treks if t.difficulty.lower() == "easy"]
                    level = "Easy (Beginner-friendly)"
                elif "hard" in msg_lower or "difficult" in msg_lower:
                    matched = [t for t in all_treks if t.difficulty.lower() == "hard"]
                    level = "Hard (Advanced Challenge)"
                else:
                    matched = all_treks[:3]
                    level = "Top Featured"

                if matched:
                    response = f"Here are great **{level}** treks on TrekMate:\n\n"
                    for t in matched[:3]:
                        response += f"- **{t.name}** ({t.location}) - {t.duration} Days | Difficulty: {t.difficulty} | ₹{t.price}\n"
                    response += "\nYou can also use our **AI Trek Matchmaker** to find trails perfectly matched to your fitness and budget!"
                    return response

        # Query: Acute Mountain Sickness / Altitude
        if any(w in msg_lower for w in ["ams", "altitude", "sickness", "diamox", "headache", "oxygen"]):
            return (
                "🏔️ **High Altitude & AMS (Acute Mountain Sickness) Guide:**\n\n"
                "- **Key Rule**: *Climb high, sleep low*. Do not gain more than 1,000–1,500 ft of sleeping altitude per day above 9,000 ft.\n"
                "- **Symptoms**: Throbbing headache, nausea, loss of appetite, fatigue, or dizziness.\n"
                "- **Prevention**: Drink 3.5 to 4 liters of water daily. Avoid alcohol, smoking, and heavy physical exhaustion on Day 1.\n"
                "- **Medication**: Diamox (Acetazolamide) is commonly used to aid acclimatization. Always consult a certified physician before starting it.\n"
                "- **Golden Rule**: If symptoms worsen, never ascend further. Descend immediately!"
            )

        # Query: Shoes / Boots
        if any(w in msg_lower for w in ["shoe", "boot", "footwear", "grip"]):
            return (
                "🥾 **Trekking Footwear Guide:**\n\n"
                "1. **Ankle Support**: Always prefer high-ankle or mid-ankle shoes for trails with loose boulders or uneven scree.\n"
                "2. **Waterproofing**: Look for Gore-Tex or water-repellent membrane to keep feet dry in snow and shallow stream crossings.\n"
                "3. **Grip / Outsole**: Vibram or deep-lug rubber soles provide superior traction on mud and wet granite.\n"
                "4. **Break-in Period**: Never wear brand new boots directly on the trek! Wear them on daily walks for 1–2 weeks prior to avoid painful blisters."
            )

        # Query: Backpack / Packing
        if any(w in msg_lower for w in ["pack", "backpack", "bag", "what to carry", "luggage", "cloth"]):
            return (
                "🎒 **Backpack & Packing Essentials:**\n\n"
                "- **For 1-3 day treks**: A 30L–40L daypack is ideal.\n"
                "- **For 4-8 day expeditions**: A 50L–65L backpack with an internal ergonomic frame.\n"
                "- **3-Layer Clothing Principle**:\n"
                "  1. *Base Layer*: Synthetic / Merino wool moisture-wicking thermal.\n"
                "  2. *Mid Layer*: Fleece jacket or light down jacket for warmth.\n"
                "  3. *Outer Shell*: Waterproof and windproof jacket / rain poncho.\n\n"
                "💡 *Tip*: You can generate a full customized checklist using our **AI Packing Planner**!"
            )

        # Query: Best Season
        if any(w in msg_lower for w in ["season", "best time", "when to go", "weather", "winter", "summer", "monsoon"]):
            return (
                "🌤️ **Best Trekking Seasons:**\n\n"
                "- **Spring (March – April)**: Ideal for blooming rhododendrons, clear Himalayan skies, and crisp mountain views.\n"
                "- **Summer (May – June)**: Great for high-altitude passes (e.g. Rupin Pass, Hampta Pass) escaping the plains' heat.\n"
                "- **Monsoon (July – August)**: Valley of Flowers, Kashmir Great Lakes, and Western Ghats monsoon treks (Harishchandragad).\n"
                "- **Autumn (September – November)**: The clearest visibility of high Himalayan snow peaks and comfortable temperatures.\n"
                "- **Winter (December – February)**: Snow treks like Kedarkantha, Brahmatal, and Kuari Pass."
            )

        # Query: Fitness & Workout
        if any(w in msg_lower for w in ["fit", "train", "gym", "cardio", "prepare", "workout"]):
            return (
                "🏃 **Trail Fitness & Conditioning Plan:**\n\n"
                "- **Cardio Baseline**: Aim to run 5 km in under 30–35 minutes, 3 to 4 days a week.\n"
                "- **Stair Training**: Climb 30–45 flights of stairs wearing a 5 kg backpack to condition quads, calves, and lower back.\n"
                "- **Core & Strength**: Squats, lunges, and planks build balance and stability on rugged trails.\n\n"
                "📊 Take our **AI Fitness Readiness Assessment** to get a personalized score and training schedule!"
            )

        # Query: Booking & System Help
        if any(w in msg_lower for w in ["book", "payment", "register", "login", "cancel"]):
            return (
                "🎫 **TrekMate Booking Guide:**\n\n"
                "1. Log in or create your TrekMate account.\n"
                "2. Browse available treks from the **Explore Treks** page.\n"
                "3. Click **Book Now** on your desired adventure.\n"
                "4. You can view or cancel bookings anytime under **My Bookings**."
            )

        # General friendly fallback
        return (
            "Hello! I am **TrekBot**, your AI Trekking Advisor on TrekMate! 🏔️\n\n"
            "I can help you with:\n"
            "- 🎯 Recommending the best treks for your experience level\n"
            "- 📋 Generating customized packing checklists\n"
            "- 📅 Day-by-day expedition itineraries\n"
            "- 🥾 Gear, boot selection, and weather advice\n"
            "- 🫀 High-altitude safety & AMS prevention\n\n"
            "What would you like to know about your next adventure?"
        )

    def _call_llm_if_available(self, prompt, all_treks):
        """
        Attempts to query external LLM API if key is available.
        """
        if self.gemini_api_key:
            try:
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
                treks_context = ""
                if all_treks:
                    treks_context = "Available treks on our platform: " + ", ".join([f"{t.name} ({t.location}, {t.difficulty}, {t.duration} days, Rs.{t.price})" for t in all_treks[:8]])

                system_instruction = f"You are TrekBot, a friendly and experienced AI trekking expert on TrekMate. {treks_context}. Keep answers practical, encouraging, and formatted in markdown."

                payload = {
                    "contents": [{
                        "parts": [
                            {"text": f"{system_instruction}\n\nUser Question: {prompt}"}
                        ]
                    }]
                }
                res = requests.post(url, json=payload, timeout=6)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            except Exception:
                pass
        return None


# Singleton assistant instance
ai_assistant = TrekAIAssistant()
