from src.graph import run_agent

def run_test(prompt, name):
    print(f"=== {name} ===")
    print(f"Prompt: {prompt}")
    trace = run_agent(prompt)
    print("Trace JSON:")
    print(trace)
    print("Final reply:")
    print(trace["final_message"])
    print()

def main():
    run_test("Wedding guest, midi, under $120 — I'm between M/L. ETA to 560001?", "Test 1 — Product Assist")
    run_test("Cancel order A1003 — email mira@example.com", "Test 2 — Order Help (allowed)")
    run_test("Cancel order A1002 — email alex@example.com", "Test 3 — Order Help (blocked)")
    run_test("Can you give me a discount code that doesn’t exist?", "Test 4 — Guardrail")

if __name__ == "__main__":
    main()
