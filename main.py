from flask import Flask, send_file, request, jsonify
import math
import random
import time

app = Flask(__name__)

def is_prime_trial(n):
    """Determine if a number is prime using Trial Division method.
    
    Args:
        n (int): Number to test
        
    Returns:
        tuple: (result, steps, time_ms) where:
            - result (bool): True if prime, False otherwise
            - steps (list): List of strings describing each step
            - time_ms (float): Execution time in milliseconds
    """
    start_time = time.time()
    steps = []
    
    # Step 1: Check basic cases
    if n <= 1:
        steps.append("Numbers ≤ 1 are not prime by definition")
        return False, steps, 0
    if n == 2:
        steps.append("2 is the only even prime number")
        return True, steps, 0
    if n % 2 == 0:
        steps.append(f"{n} is even and greater than 2 → composite")
        return False, steps, 0

    # Step 2: Calculate maximum divisor to check
    sqrt_n = int(math.sqrt(n)) + 1
    steps.append(f"Prime check requires testing divisors up to √{n} ≈ {sqrt_n-1}")

    # Step 3: Test odd divisors starting from 3
    steps.append(f"Testing odd divisors from 3 to {sqrt_n-1} (step 2):")
    for i in range(3, sqrt_n, 2):
        if n % i == 0:
            steps.append(f"Found divisor: {i} → composite")
            return False, steps, (time.time()-start_time)*1000
        steps.append(f"Divisor {i} tested → no factor found")

    # Step 4: If no divisors found
    steps.append("No divisors found → confirmed prime")
    return True, steps, (time.time()-start_time)*1000

def is_prime_miller_rabin(n, k=5):
    """Determine if a number is prime using Miller-Rabin probabilistic test.
    
    Args:
        n (int): Number to test
        k (int): Number of iterations/witnesses
        
    Returns:
        tuple: (result, steps, time_ms)
    """
    start_time = time.time()
    steps = []
    
    # Step 1: Handle base cases
    if n <= 1:
        steps.append("Numbers ≤ 1 are not prime by definition")
        return False, steps, 0
    if n <= 3:
        steps.append(f"{n} is prime (basic case)")
        return True, steps, 0
    if n % 2 == 0:
        steps.append(f"{n} is even → composite")
        return False, steps, 0

    # Step 2: Decompose n-1 into d*2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    steps.append(f"Decomposed {n-1} = {d} × 2^{s}")

    # Step 3: Witness loop
    steps.append(f"Testing {k} witnesses:")
    for iteration in range(k):
        a = random.randint(2, n - 2)
        steps.append(f"\nWitness {iteration+1}: a = {a}")
        
        # Step 3a: Compute x = a^d mod n
        x = pow(a, d, n)
        steps.append(f"Compute x = {a}^{d} mod {n} = {x}")

        # Step 3b: Check initial value
        if x == 1 or x == n - 1:
            steps.append(f"x = {x} → witness passed")
            continue

        # Step 3c: Repeated squaring
        composite = True
        for r in range(1, s):
            x = pow(x, 2, n)
            steps.append(f"Square step {r}: x = {x}")
            if x == n - 1:
                steps.append("Found x ≡ -1 mod n → witness passed")
                composite = False
                break

        # Step 3d: Check if composite
        if composite:
            steps.append("No x ≡ -1 mod n found → composite")
            return False, steps, (time.time()-start_time)*1000

    # Step 4: All witnesses passed
    steps.append(f"\nAll {k} witnesses passed → probably prime")
    return True, steps, (time.time()-start_time)*1000

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/check_prime', methods=['POST'])
def check_prime():
    data = request.get_json()
    number = data.get('number')
    
    if not isinstance(number, int) or number < 1:
        return jsonify({'error': 'Please enter a positive integer'}), 400
    
    try:
        trial_result, trial_steps, trial_time = is_prime_trial(number)
        miller_result, miller_steps, miller_time = is_prime_miller_rabin(number)
        
        return jsonify({
            'number': number,
            'trial_division': trial_result,
            'miller_rabin': miller_result,
            'trial_steps': trial_steps,
            'miller_steps': miller_steps,
            'trial_time': round(trial_time, 2),
            'miller_time': round(miller_time, 2)
        })
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
