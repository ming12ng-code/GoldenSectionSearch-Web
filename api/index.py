from http.server import BaseHTTPRequestHandler
import json
import math
import urllib.parse


# =========================================================
# Evaluate objective function
# =========================================================

def evaluate_function(function_string, x):

    # Convert common mathematical notation
    expression = function_string

    expression = expression.replace("^", "**")

    allowed = {
        "__builtins__": {},

        "x": x,

        "math": math,

        # Logarithm
        "ln": math.log,
        "log": math.log,

        # Other common functions
        "exp": math.exp,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,

        # Constants
        "pi": math.pi,
        "e": math.e
    }

    return eval(
        expression,
        allowed
    )


# =========================================================
# Golden Section Search
# =========================================================

def golden_section_search(
    function_string,
    start,
    end,
    tolerance
):

    phi = (math.sqrt(5) - 1) / 2

    a = start
    b = end

    initial_length = b - a

    # Theoretical K
    theoretical_k = math.ceil(
        math.log(
            tolerance / initial_length
        )
        /
        math.log(phi)
    )

    iteration_table = []

    iteration = 0

    while abs(b - a) > tolerance:

        iteration += 1

        x1 = b - phi * (b - a)

        x2 = a + phi * (b - a)

        f_x1 = evaluate_function(
            function_string,
            x1
        )

        f_x2 = evaluate_function(
            function_string,
            x2
        )

        if f_x1 < f_x2:

            b = x2

        else:

            a = x1

        iteration_table.append({

            "iteration": iteration,

            "x1": x1,

            "x2": x2,

            "f(x1)": f_x1,

            "f(x2)": f_x2,

            "a": a,

            "b": b,

            "interval_length": b - a

        })


    # Approximate minimum

    x_min = (a + b) / 2

    f_min = evaluate_function(
        function_string,
        x_min
    )


    return {

        "minimum_x": x_min,

        "minimum_f": f_min,

        "iterations": iteration,

        "theoretical_k": theoretical_k,

        "final_interval": [
            a,
            b
        ],

        "iteration_table": iteration_table

    }


# =========================================================
# Vercel API
# =========================================================

class handler(BaseHTTPRequestHandler):


    def do_GET(self):

        try:

            # Read URL parameters

            parsed_url = urllib.parse.urlparse(
                self.path
            )

            query = urllib.parse.parse_qs(
                parsed_url.query
            )


            # Get user inputs

            function_string = query.get(
                "function",
                ["ln(x)-4*x+5"]
            )[0]


            start = float(
                query.get(
                    "start",
                    ["1"]
                )[0]
            )


            end = float(
                query.get(
                    "end",
                    ["10"]
                )[0]
            )


            tolerance = float(
                query.get(
                    "tolerance",
                    ["0.0001"]
                )[0]
            )


            # Validate interval

            if start >= end:

                raise ValueError(
                    "Start of interval must be less than end."
                )


            if tolerance <= 0:

                raise ValueError(
                    "Tolerance must be greater than zero."
                )


            # =================================================
            # Check function domain
            # =================================================

            test_points = [

                start,

                start + (end - start) * 0.25,

                start + (end - start) * 0.5,

                start + (end - start) * 0.75,

                end

            ]


            for test_x in test_points:

                test_y = evaluate_function(
                    function_string,
                    test_x
                )

                if not math.isfinite(test_y):

                    raise ValueError(
                        "The function is not valid in this interval."
                    )


            # =================================================
            # Run Golden Section Search
            # =================================================

            result = golden_section_search(

                function_string,

                start,

                end,

                tolerance

            )


            # =================================================
            # Send JSON response
            # =================================================

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


        except Exception as error:


            response = json.dumps({

                "error": str(error)

            })


            self.send_response(400)


            self.send_header(
                "Content-Type",
                "application/json"
            )


            self.end_headers()


            self.wfile.write(
                response.encode()
            )
