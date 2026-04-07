
#EASY TASKS (GENUINE)


easy_cases = [
    {
        "query": "I received a damaged product, want a refund",
        "days": 2,
        "has_proof": True,
        "correct_action": "refund"
    },
    {
        "query": "The item is broken, can I get a replacement?",
        "days": 1,
        "has_proof": True,
        "correct_action": "replace"
    },
    {
        "query": "Wrong item delivered, I ordered something else",
        "days": 3,
        "has_proof": True,
        "correct_action": "replace"
    },
    {
        "query": "Product stopped working within 5 days",
        "days": 5,
        "has_proof": True,
        "correct_action": "refund"
    },
    {
        "query": "I want to return the product, it is defective",
        "days": 6,
        "has_proof": True,
        "correct_action": "refund"
    }
]


#MEDIUM TASKS (LYING / POLICY)


medium_cases = [
    {
        "query": "I never received my order but tracking says delivered",
        "days": 4,
        "has_proof": False,
        "correct_action": "reject"
    },
    {
        "query": "Product is damaged (no images attached)",
        "days": 3,
        "has_proof": False,
        "correct_action": "ask_proof"
    },
    {
        "query": "I want refund but I already used the product",
        "days": 5,
        "has_proof": False,
        "correct_action": "reject"
    },
    {
        "query": "Claiming wrong item but order history matches delivery",
        "days": 2,
        "has_proof": False,
        "correct_action": "reject"
    },
    {
        "query": "Requesting refund after clearly using the product",
        "days": 4,
        "has_proof": False,
        "correct_action": "reject"
    }
]


# HARD TASKS (SUSPICIOUS)


hard_cases = [
    {
        "query": "Product seems damaged but not sure",
        "days": 2,
        "has_proof": False,
        "correct_action": "ask_proof"
    },
    {
        "query": "I think I got a defective item",
        "days": 3,
        "has_proof": False,
        "correct_action": "ask_proof"
    },
    {
        "query": "Item not working properly, can you help?",
        "days": 4,
        "has_proof": False,
        "correct_action": "ask_proof"
    },
    {
        "query": "Received product but facing issues",
        "days": 5,
        "has_proof": False,
        "correct_action": "ask_proof"
    },
    {
        "query": "The product quality is not good",
        "days": 6,
        "has_proof": False,
        "correct_action": "ask_proof"
    }
]