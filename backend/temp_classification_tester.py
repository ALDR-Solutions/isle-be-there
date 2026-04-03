"""
Temporary classification tester for review classification functionality.
Tests both ML classifier and keyword classifier with test data from hotel-reviews.
"""

import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import ML classifier
from app.modules.reviews.review_classifier import classify_review
from app.modules.reviews.keyword_classifier import BUSINESS_TYPE_UUIDS

# Import keyword classifier
from app.modules.reviews.keyword_classifier import classify_with_keywords, check_flags

# Get HOTEL_UUID and RESTAURANT_UUID from BUSINESS_TYPE_UUIDS
HOTEL_UUID = BUSINESS_TYPE_UUIDS["hotel"]
RESTAURANT_UUID = BUSINESS_TYPE_UUIDS["restaurant"]

# Hotel test reviews (from hotel-reviews run_unified_pipeline.py)
HOTEL_TEST_REVIEWS = [
    {"text": "Excellent location in the heart of downtown. The staff was incredibly friendly and helpful.", "expected_topics": ["location", "service"]},
    {"text": "Room was spotless and very comfortable. Great value for the price.", "expected_topics": ["clean", "value"]},
    {"text": "The breakfast buffet was amazing with so many options!", "expected_topics": ["food"]},
    {"text": "Beautiful room with amazing views. Very quiet at night.", "expected_topics": ["room", "other"]},
    {"text": "Room was too small for a family. Noisy street below made sleeping difficult.", "expected_topics": ["room", "other"]},
    # French
    {"text": "Excellent emplacement, personnel tres aimable, chambre propre.", "expected_topics": ["location", "service", "clean"]},
    {"text": "Le petit-dejeuner etait excellent avec beaucoup de choix.", "expected_topics": ["food"]},
    {"text": "Chambre confortable mais un peu bruyante le matin.", "expected_topics": ["room", "other"]},
    # Spanish
    {"text": "Gran ubicacion, personal amable, habitaciones limpias. El desayuno estaba delicioso.", "expected_topics": ["location", "service", "clean", "food"]},
    {"text": "La habitacion era espaciosa con buenas vistas.", "expected_topics": ["room", "other"]},
    # Dutch
    {"text": "Uitstekende locatie, vriendelijk personeel, schone kamers.", "expected_topics": ["location", "service", "clean"]},
    {"text": "Heerlijk ontbijt met veel verse producten.", "expected_topics": ["food"]},
]

# Restaurant test reviews (from hotel-reviews run_unified_pipeline.py)
RESTAURANT_TEST_REVIEWS = [
    {"text": "The food here is absolutely amazing! Best pasta I've ever had.", "expected_topics": ["food_quality"]},
    {"text": "Amazing ambience with soft lighting and romantic music. Perfect for dates.", "expected_topics": ["ambience"]},
    {"text": "Waited 45 minutes for a table despite having a reservation. Very disappointing.", "expected_topics": ["wait_time"]},
    {"text": "Staff was incredibly attentive and professional. Made our anniversary special.", "expected_topics": ["service_quality"]},
    {"text": "Clean restaurant with proper hygiene protocols. Felt safe dining here.", "expected_topics": ["cleanliness", "hygiene_safety"]},
    # French
    {"text": "La qualite de la nourriture etait exceptionnelle. Les desserts etaient divins!", "expected_topics": ["food_quality"]},
    {"text": "Ambiance romantique avec un service impeccable. Je recommande!", "expected_topics": ["ambience", "service_quality"]},
    {"text": "Temps d'attente trop long, mais la nourriture valait le detour.", "expected_topics": ["wait_time", "food_quality"]},
    # Spanish
    {"text": "La comida estaba deliciosa! Los platos principales estaban perfectamente cocinados.", "expected_topics": ["food_quality"]},
    {"text": "Excelente ambiente y atencion al cliente. Volveremos seguro.", "expected_topics": ["ambience", "service_quality"]},
    {"text": "Buena relacion calidad-precio para la comida que sirven.", "expected_topics": ["value_for_money", "food_quality"]},
    # Dutch
    {"text": "Heerlijk eten en uitstekende service. Een aanrader!", "expected_topics": ["food_quality", "service_quality"]},
    {"text": "Sfeer is gezellig, eten smaakvol. Wel lange wachttijd.", "expected_topics": ["ambience", "wait_time"]},
]


def test_ml_classification():
    """Test ML classification for Hotel and Restaurant reviews."""
    print("\n" + "=" * 70)
    print("ML CLASSIFICATION TEST")
    print("=" * 70)
    
    # Test Hotel classification
    print("\n[HOTEL CLASSIFICATION]")
    print("-" * 50)
    
    hotel_correct = 0
    hotel_total = len(HOTEL_TEST_REVIEWS)
    
    for review in HOTEL_TEST_REVIEWS:
        text = review["text"]
        expected = review["expected_topics"]
        
        result = classify_review(text, HOTEL_UUID)
        predicted = result.get("main_label", "(none)")
        expected_main = expected[0]
        
        is_correct = predicted == expected_main
        if is_correct:
            hotel_correct += 1
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} \"{text[:50]}...\"" if len(text) > 50 else f"  {status} \"{text}\"")
        print(f"      Expected: {expected_main}, Predicted: {predicted}")
    
    hotel_accuracy = (hotel_correct / hotel_total) * 100 if hotel_total > 0 else 0
    print(f"\n  Hotel Accuracy (Label-1): {hotel_correct}/{hotel_total} ({hotel_accuracy:.1f}%)")
    
    # Test Restaurant classification
    print("\n[RESTAURANT CLASSIFICATION]")
    print("-" * 50)
    
    rest_correct = 0
    rest_total = len(RESTAURANT_TEST_REVIEWS)
    
    for review in RESTAURANT_TEST_REVIEWS:
        text = review["text"]
        expected = review["expected_topics"]
        
        result = classify_review(text, RESTAURANT_UUID)
        predicted = result.get("main_label", "(none)")
        expected_main = expected[0]
        
        is_correct = predicted == expected_main
        if is_correct:
            rest_correct += 1
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} \"{text[:50]}...\"" if len(text) > 50 else f"  {status} \"{text}\"")
        print(f"      Expected: {expected_main}, Predicted: {predicted}")
    
    rest_accuracy = (rest_correct / rest_total) * 100 if rest_total > 0 else 0
    print(f"\n  Restaurant Accuracy (Label-1): {rest_correct}/{rest_total} ({rest_accuracy:.1f}%)")
    
    # Combined summary
    total = hotel_total + rest_total
    total_correct = hotel_correct + rest_correct
    combined_accuracy = (total_correct / total) * 100 if total > 0 else 0
    
    print("\n" + "-" * 50)
    print(f"COMBINED ML ACCURACY: {total_correct}/{total} ({combined_accuracy:.1f}%)")
    
    return {
        "hotel_correct": hotel_correct,
        "hotel_total": hotel_total,
        "hotel_accuracy": hotel_accuracy,
        "rest_correct": rest_correct,
        "rest_total": rest_total,
        "rest_accuracy": rest_accuracy,
        "total_correct": total_correct,
        "total": total,
        "combined_accuracy": combined_accuracy,
    }


def test_keyword_classification():
    """Test keyword classification for Events, Tours, and Services."""
    print("\n" + "=" * 70)
    print("KEYWORD CLASSIFICATION TEST")
    print("=" * 70)
    
    # Sample reviews for each business type
    events_reviews = [
        {"text": "Amazing vibes at this venue! Great music and electric atmosphere.", "expected_main": "atmosphere"},
        {"text": "The DJ was awesome and the live band was incredible.", "expected_main": "entertainment"},
        {"text": "Well organized event with smooth entry. Great value for the price.", "expected_main": "organisation"},
        {"text": "Felt safe with good security. Easy to find location.", "expected_main": "safety"},
        {"text": "Delicious cocktails and great drinks at the bar.", "expected_main": "food_drinks"},
    ]
    
    tours_reviews = [
        {"text": "Our tour guide was knowledgeable and very friendly.", "expected_main": "guide_quality"},
        {"text": "The historical value of this tour was fascinating.", "expected_main": "historical_value"},
        {"text": "Clean facilities and wheelchair accessible.", "expected_main": "facilities"},
        {"text": "Worth every penny, great value tour.", "expected_main": "value"},
        {"text": "Beautiful scenery and breathtaking views.", "expected_main": "atmosphere"},
    ]
    
    services_reviews = [
        {"text": "Staff was friendly and professional. Excellent service overall.", "expected_main": "service_quality"},
        {"text": "Fast and efficient service. No wait time at all.", "expected_main": "efficiency"},
        {"text": "Great quality work, perfectly done.", "expected_main": "quality"},
        {"text": "Fair price and great value for the service.", "expected_main": "value"},
        {"text": "Easy booking with clear communication throughout.", "expected_main": "communication"},
    ]
    
    # Test Events
    print("\n[EVENTS CLASSIFICATION]")
    print("-" * 50)
    events_uuid = BUSINESS_TYPE_UUIDS["events"]
    
    events_correct = 0
    for review in events_reviews:
        text = review["text"]
        expected = review["expected_main"]
        
        result = classify_with_keywords(text, events_uuid)
        predicted = result.get("main_label", "(none)")
        
        is_correct = predicted == expected
        if is_correct:
            events_correct += 1
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} \"{text[:40]}...\"" if len(text) > 40 else f"  {status} \"{text}\"")
        print(f"      Expected: {expected}, Predicted: {predicted}")
    
    events_accuracy = (events_correct / len(events_reviews)) * 100 if events_reviews else 0
    print(f"\n  Events Accuracy (Label-1): {events_correct}/{len(events_reviews)} ({events_accuracy:.1f}%)")
    
    # Test Tours
    print("\n[TOURS CLASSIFICATION]")
    print("-" * 50)
    tours_uuid = BUSINESS_TYPE_UUIDS["tours"]
    
    tours_correct = 0
    for review in tours_reviews:
        text = review["text"]
        expected = review["expected_main"]
        
        result = classify_with_keywords(text, tours_uuid)
        predicted = result.get("main_label", "(none)")
        
        is_correct = predicted == expected
        if is_correct:
            tours_correct += 1
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} \"{text[:40]}...\"" if len(text) > 40 else f"  {status} \"{text}\"")
        print(f"      Expected: {expected}, Predicted: {predicted}")
    
    tours_accuracy = (tours_correct / len(tours_reviews)) * 100 if tours_reviews else 0
    print(f"\n  Tours Accuracy (Label-1): {tours_correct}/{len(tours_reviews)} ({tours_accuracy:.1f}%)")
    
    # Test Services
    print("\n[SERVICES CLASSIFICATION]")
    print("-" * 50)
    services_uuid = BUSINESS_TYPE_UUIDS["services"]
    
    services_correct = 0
    for review in services_reviews:
        text = review["text"]
        expected = review["expected_main"]
        
        result = classify_with_keywords(text, services_uuid)
        predicted = result.get("main_label", "(none)")
        
        is_correct = predicted == expected
        if is_correct:
            services_correct += 1
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} \"{text[:40]}...\"" if len(text) > 40 else f"  {status} \"{text}\"")
        print(f"      Expected: {expected}, Predicted: {predicted}")
    
    services_accuracy = (services_correct / len(services_reviews)) * 100 if services_reviews else 0
    print(f"\n  Services Accuracy (Label-1): {services_correct}/{len(services_reviews)} ({services_accuracy:.1f}%)")
    
    # Combined summary
    total_tests = len(events_reviews) + len(tours_reviews) + len(services_reviews)
    total_correct = events_correct + tours_correct + services_correct
    combined_accuracy = (total_correct / total_tests) * 100 if total_tests > 0 else 0
    
    print("\n" + "-" * 50)
    print(f"COMBINED KEYWORD ACCURACY: {total_correct}/{total_tests} ({combined_accuracy:.1f}%)")
    
    return {
        "events_correct": events_correct,
        "events_total": len(events_reviews),
        "events_accuracy": events_accuracy,
        "tours_correct": tours_correct,
        "tours_total": len(tours_reviews),
        "tours_accuracy": tours_accuracy,
        "services_correct": services_correct,
        "services_total": len(services_reviews),
        "services_accuracy": services_accuracy,
        "total_correct": total_correct,
        "total": total_tests,
        "combined_accuracy": combined_accuracy,
    }


def test_flag_detection():
    """Test flag detection for profanity, hate speech, spam, and personal attacks."""
    print("\n" + "=" * 70)
    print("FLAG DETECTION TEST")
    print("=" * 70)
    
    # Profanity test cases
    profanity_tests = [
        {"text": "This place was fucking amazing!", "should_flag": True},
        {"text": "The service was shit and I hate it.", "should_flag": True},
        {"text": "What a damn good time we had.", "should_flag": True},
        {"text": "Absolutely wonderful experience.", "should_flag": False},
    ]
    
    # Hate speech test cases
    hate_tests = [
        {"text": "I hate them and they should die.", "should_flag": True},
        {"text": "They are worthless and should rot in hell.", "should_flag": True},
        {"text": "The worst experience I've ever had.", "should_flag": False},
        {"text": "I really hate waiting in line.", "should_flag": False},
    ]
    
    # Spam test cases
    spam_tests = [
        {"text": "Click here to buy now and get a free vacation!", "should_flag": True},
        {"text": "Congratulations! You are a winner. Act now!", "should_flag": True},
        {"text": "Great restaurant, will visit again.", "should_flag": False},
        {"text": "Limited time offer on our services.", "should_flag": False},
    ]
    
    # Personal attack test cases
    attack_tests = [
        {"text": "The staff were idiots and the manager is stupid.", "should_flag": True},
        {"text": "What a dumb decision by that moron.", "should_flag": True},
        {"text": "The food was tasty and well prepared.", "should_flag": False},
        {"text": "Somewhat disappointed with the service.", "should_flag": False},
    ]
    
    all_tests_passed = True
    
    # Test profanity
    print("\n[PROFANITY DETECTION]")
    print("-" * 50)
    profanity_passed = 0
    for test in profanity_tests:
        result = check_flags(test["text"])
        detected = result["is_flagged"]
        expected = test["should_flag"]
        is_correct = detected == expected
        if is_correct:
            profanity_passed += 1
        else:
            all_tests_passed = False
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} \"{test['text'][:40]}...\"" if len(test["text"]) > 40 else f"  {status} \"{test['text']}\"")
        print(f"      Expected flagged: {expected}, Detected: {detected}")
    
    print(f"\n  Profanity Accuracy: {profanity_passed}/{len(profanity_tests)} ({100*profanity_passed/len(profanity_tests):.1f}%)")
    
    # Test hate speech
    print("\n[HATE SPEECH DETECTION]")
    print("-" * 50)
    hate_passed = 0
    for test in hate_tests:
        result = check_flags(test["text"])
        detected = result["is_flagged"]
        expected = test["should_flag"]
        is_correct = detected == expected
        if is_correct:
            hate_passed += 1
        else:
            all_tests_passed = False
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} \"{test['text'][:40]}...\"" if len(test["text"]) > 40 else f"  {status} \"{test['text']}\"")
        print(f"      Expected flagged: {expected}, Detected: {detected}")
    
    print(f"\n  Hate Speech Accuracy: {hate_passed}/{len(hate_tests)} ({100*hate_passed/len(hate_tests):.1f}%)")
    
    # Test spam
    print("\n[SPAM DETECTION]")
    print("-" * 50)
    spam_passed = 0
    for test in spam_tests:
        result = check_flags(test["text"])
        detected = result["is_flagged"]
        expected = test["should_flag"]
        is_correct = detected == expected
        if is_correct:
            spam_passed += 1
        else:
            all_tests_passed = False
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} \"{test['text'][:40]}...\"" if len(test["text"]) > 40 else f"  {status} \"{test['text']}\"")
        print(f"      Expected flagged: {expected}, Detected: {detected}")
    
    print(f"\n  Spam Accuracy: {spam_passed}/{len(spam_tests)} ({100*spam_passed/len(spam_tests):.1f}%)")
    
    # Test personal attacks
    print("\n[PERSONAL ATTACK DETECTION]")
    print("-" * 50)
    attack_passed = 0
    for test in attack_tests:
        result = check_flags(test["text"])
        detected = result["is_flagged"]
        expected = test["should_flag"]
        is_correct = detected == expected
        if is_correct:
            attack_passed += 1
        else:
            all_tests_passed = False
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} \"{test['text'][:40]}...\"" if len(test["text"]) > 40 else f"  {status} \"{test['text']}\"")
        print(f"      Expected flagged: {expected}, Detected: {detected}")
    
    print(f"\n  Personal Attack Accuracy: {attack_passed}/{len(attack_tests)} ({100*attack_passed/len(attack_tests):.1f}%)")
    
    # Combined summary
    total_tests = len(profanity_tests) + len(hate_tests) + len(spam_tests) + len(attack_tests)
    total_passed = profanity_passed + hate_passed + spam_passed + attack_passed
    combined_accuracy = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print("\n" + "-" * 50)
    print(f"COMBINED FLAG DETECTION ACCURACY: {total_passed}/{total_tests} ({combined_accuracy:.1f}%)")
    
    return {
        "profanity_passed": profanity_passed,
        "profanity_total": len(profanity_tests),
        "hate_passed": hate_passed,
        "hate_total": len(hate_tests),
        "spam_passed": spam_passed,
        "spam_total": len(spam_tests),
        "attack_passed": attack_passed,
        "attack_total": len(attack_tests),
        "total_passed": total_passed,
        "total": total_tests,
        "combined_accuracy": combined_accuracy,
    }


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("REVIEW CLASSIFICATION TESTING SUITE")
    print("=" * 70)
    print(f"\nHOTEL_UUID: {HOTEL_UUID}")
    print(f"RESTAURANT_UUID: {RESTAURANT_UUID}")
    print(f"BUSINESS_TYPE_UUIDS: {BUSINESS_TYPE_UUIDS}")
    
    # Run all tests
    ml_results = test_ml_classification()
    keyword_results = test_keyword_classification()
    flag_results = test_flag_detection()
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"\n  ML Classification (Hotel+Restaurant):")
    print(f"    - Hotel:     {ml_results['hotel_correct']}/{ml_results['hotel_total']} ({ml_results['hotel_accuracy']:.1f}%)")
    print(f"    - Restaurant: {ml_results['rest_correct']}/{ml_results['rest_total']} ({ml_results['rest_accuracy']:.1f}%)")
    print(f"    - Combined:  {ml_results['total_correct']}/{ml_results['total']} ({ml_results['combined_accuracy']:.1f}%)")
    
    print(f"\n  Keyword Classification (Events+Tours+Services):")
    print(f"    - Events:    {keyword_results['events_correct']}/{keyword_results['events_total']} ({keyword_results['events_accuracy']:.1f}%)")
    print(f"    - Tours:     {keyword_results['tours_correct']}/{keyword_results['tours_total']} ({keyword_results['tours_accuracy']:.1f}%)")
    print(f"    - Services:  {keyword_results['services_correct']}/{keyword_results['services_total']} ({keyword_results['services_accuracy']:.1f}%)")
    print(f"    - Combined:  {keyword_results['total_correct']}/{keyword_results['total']} ({keyword_results['combined_accuracy']:.1f}%)")
    
    print(f"\n  Flag Detection:")
    print(f"    - Profanity:      {flag_results['profanity_passed']}/{flag_results['profanity_total']}")
    print(f"    - Hate Speech:    {flag_results['hate_passed']}/{flag_results['hate_total']}")
    print(f"    - Spam:           {flag_results['spam_passed']}/{flag_results['spam_total']}")
    print(f"    - Personal Attack: {flag_results['attack_passed']}/{flag_results['attack_total']}")
    print(f"    - Combined:       {flag_results['total_passed']}/{flag_results['total']} ({flag_results['combined_accuracy']:.1f}%)")
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)