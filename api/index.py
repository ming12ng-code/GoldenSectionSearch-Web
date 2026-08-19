from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import math


# ============================================================
# Evaluate mathematical function
# ============================================================

def evaluate_function(expression, x):

    expression = expression.replace("^", "**")

    allowed_functions = {
        "x": x,
        "ln": math.log,
        "log": math.log,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "exp": math.exp,
        "sqrt": math.sqrt,
        "abs": abs,
        "pi": math.pi,
        "e": math.e
    }

    return eval(
        expression,
        {"__builtins__": {}},
        allowed_functions
    )


# ============================================================
# Golden Section Search
# ============================================================

def golden_section_search(
    expression,
    a,
    b,
    tolerance,
    optimization_type
):

    phi = (1 + math.sqrt(5)) / 2

    # Theoretical number of iterations
    theoretical_k = math.ceil(
        math.log(
            tolerance / abs(b - a)
        )
        /
        math.log(1 / phi)
    )

    # Initial points
    x1 = b - (b - a) / phi
    x2 = a + (b - a) / phi

    f1 = evaluate_function(
        expression,
        x1
    )

    f2 = evaluate_function(
        expression,
        x2
    )

    iteration_table = []

    iteration = 0


    # ========================================================
    # Search
    # ========================================================

    while abs(b - a) > tolerance:

        iteration += 1


        # ----------------------------------------------------
        # MINIMUM
        # ----------------------------------------------------

        if optimization_type == "minimum":

            if f1 < f2:

                b = x2

                x2 = x1

                f2 = f1

                x1 = b - (b - a) / phi

                f1 = evaluate_function(
                    expression,
                    x1
                )

            else:

                a = x1

                x1 = x2

                f1 = f2

                x2 = a + (b - a) / phi

                f2 = evaluate_function(
                    expression,
                    x2
                )


        # ----------------------------------------------------
        # MAXIMUM
        # ----------------------------------------------------

        elif optimization_type == "maximum":

            if f1 > f2:

                b = x2

                x2 = x1

                f2 = f1

                x1 = b - (b - a) / phi

                f1 = evaluate_function(
                    expression,
                    x1
                )

            else:

                a = x1

                x1 = x2

                f1 = f2

                x2 = a + (b - a) / phi

                f2 = evaluate_function(
                    expression,
                    x2
                )


        # ----------------------------------------------------
        # Save iteration
        # ----------------------------------------------------

        iteration_table.append({

            "iteration": iteration,

            "x1": x1,

            "x2": x2,

            "f(x1)": f1,

            "f(x2)": f2,

            "a": a,

            "b": b,

            "interval_length": abs(b - a)

        })


    # ========================================================
    # Final result
    # ========================================================

    if optimization_type == "minimum":

        if f1 < f2:

            minimum_x = x1
            minimum_f = f1

        else:

            minimum_x = x2
            minimum_f = f2


    else:

        if f1 > f2:

            minimum_x = x1
            minimum_f = f1

        else:

            minimum_x = x2
            minimum_f = f2


    return {

        "minimum_x": minimum_x,

        "minimum_f": minimum_f,

        "iterations": iteration,

        "theoretical_k": theoretical_k,

        "final_interval": [
            a,
            b
        ],

        "iteration_table": iteration_table

    }


# ============================================================
# Vercel API
# ============================================================

class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:

            # ------------------------------------------------
            # Read query parameters
            # ------------------------------------------------

            query = urllib.parse.urlparse(
                self.path
            ).query

            params = urllib.parse.parse_qs(
                query
            )


            expression = params.get(
                "function",
                ["x**2"]
            )[0]


            a = float(
                params.get(
                    "start",
                    ["0"]
                )[0]
            )


            b = float(
                params.get(
                    "end",
                    ["10"]
                )[0]
            )


            tolerance = float(
                params.get(
                    "tolerance",
                    ["0.0001"]
                )[0]
            )


            optimization_type = params.get(
                "type",
                ["minimum"]
            )[0]


            # ------------------------------------------------
            # Run Golden Section Search
            # ------------------------------------------------

            result = golden_section_search(

                expression,

                a,

                b,

                tolerance,

                optimization_type

            )


            # ------------------------------------------------
            # Return JSON
            # ------------------------------------------------

            response = json.dumps(
                result
            )


            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()


            self.wfile.write(
                response.encode()
            )


        except Exception as e:

            self.send_response(400)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()


            error_response = json.dumps({

                "error": str(e)

            })


            self.wfile.write(
                error_response.encode()
            )
