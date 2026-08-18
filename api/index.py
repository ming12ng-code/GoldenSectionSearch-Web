from http.server import BaseHTTPRequestHandler
import json
import math


def golden_section_search(function_string, start, end, tolerance):

    # Allow common mathematical functions
    allowed_functions = {
        "math": math,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "exp": math.exp,
        "log": math.log,
        "ln": math.log
    }

    # Create objective function
    def f(x):
        return eval(
            function_string,
            {
                "__builtins__": None,
                "x": x,
                **allowed_functions
            }
        )

    # Golden ratio
    phi = (math.sqrt(5) - 1) / 2

    # Initial interval
    a = start
    b = end

    initial_interval_length = b - a

    # Theoretical K
    if tolerance >= initial_interval_length:
        theoretical_k = 0
    else:
        theoretical_k = math.ceil(
            math.log(tolerance / initial_interval_length)
            / math.log(phi)
        )

    # Iteration table
    iteration_table = []

    k = 0

    while abs(b - a) > tolerance:

        k += 1

        x1 = b - phi * (b - a)
        x2 = a + phi * (b - a)

        f_x1 = f(x1)
        f_x2 = f(x2)

        if f_x1 < f_x2:
            b = x2
        else:
            a = x1

        iteration_table.append({
            "iteration": k,
            "x1": x1,
            "x2": x2,
            "f(x1)": f_x1,
            "f(x2)": f_x2,
            "a": a,
            "b": b,
            "interval_length": b - a
        })

    # Final result
    x_min = (a + b) / 2
    f_min = f(x_min)

    return {
        "function": function_string,
        "initial_interval": [start, end],
        "tolerance": tolerance,
        "minimum_x": x_min,
        "minimum_f": f_min,
        "iterations": k,
        "theoretical_k": theoretical_k,
        "final_interval": [a, b],
        "iteration_table": iteration_table
    }


class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:

            # Example test values for now
            function_string = "ln(x)-4*x+5"
            start = 1
            end = 10
            tolerance = 0.0001

            result = golden_section_search(
                function_string,
                start,
                end,
                tolerance
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps(result).encode()
            )

        except Exception as error:

            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {
                "error": str(error)
            }

            self.wfile.write(
                json.dumps(response).encode()
            )
