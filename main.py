from flask import Flask, render_template, request, jsonify
import math
import random
import time

app = Flask(__name__)

def is_prime_trial(n):
    start = time.time()
    steps = []
    if n <= 1:
        steps.append(f"{n} is not prime (≤1)")
        return False, steps, 0
    if n == 2:
        steps.append("2 is prime")
        return True, steps, 0
    if n % 2 == 0:
        steps.append(f"{n} is even → composite")
        return False, steps, 0
    
    sqrt_n = int(math.sqrt(n)) + 1
    steps.append(f"Checking divisors from 3 to {sqrt_n}")
    
    for i in range(3, sqrt_n, 2):
        if n % i == 0:
            steps.append(f"Found divisor: {i} → composite")
            return False, steps, time.time()-start
        steps.append(f"Tested divisor: {i} ✓")
    
    steps.append(f"No divisors found → prime")
    return True, steps, (time.time()-start)*1000

def is_prime_miller_rabin(n, k=5):
    start = time.time()
    steps = []
    if n <= 1:
        steps.append(f"{n} is not prime (≤1)")
        return False, steps, 0
    if n <= 3:
        steps.append(f"{n} is prime (≤3)")
        return True, steps, 0
    if n % 2 == 0:
        steps.append(f"{n} is even → composite")
        return False, steps, 0

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    steps.append(f"Decomposition: {n-1} = {d} × 2^{s}")

    for i in range(k):
        a = random.randint(2, n - 2)
        steps.append(f"\nWitness {i+1}: a = {a}")
        x = pow(a, d, n)
        steps.append(f"Compute x = a^d mod n → {x}")
        
        if x == 1 or x == n - 1:
            steps.append(f"x = {x} → continue")
            continue
            
        composite = True
        for r in range(1, s):
            x = pow(x, 2, n)
            steps.append(f"Step {r}: x = x² mod n → {x}")
            if x == n - 1:
                steps.append("Found x = -1 mod n → continue")
                composite = False
                break
                
        if composite:
            steps.append("No x = -1 mod n found → composite")
            return False, steps, (time.time()-start)*1000
        else:
            steps.append("Witness passed")
    
    steps.append(f"\nAll {k} witnesses passed → probably prime")
    return True, steps, (time.time()-start)*1000

@app.route('/')
def index():
    return render_template('index.html')

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
