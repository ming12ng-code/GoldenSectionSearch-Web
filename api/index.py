from http.server import BaseHTTPRequestHandler
import json
import math
import urllib.parse


def evaluate_function(function_string, x):

    allowed = {
        "__builtins__": {},
        "x": x,
        "math": math,
        "ln": math.log,
        "log": math.log,
        "exp": math.exp,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan
    }

    return eval(function_string, allowed)


def golden_section_search(function_string, start, end, tolerance):

    phi = (math.sqrt(5) - 1) / 2

    a = start
    b = end

    initial_length = b - a

    # Theoretical K
    theoretical_k = math.ceil(
        math.log(tolerance / initial_length)
        / math.log(phi)
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


def generate_graph_data(
    function_string,
    start,
    end
):

    interval = end - start

    graph_start = start - interval * 0.1

    graph_end = end + interval * 0.1

    number_of_points = 500

    x_values = []

    y_values = []

    for i in range(number_of_points):

        x = (
            graph_start
            +
            (
                graph_end - graph_start
            )
            * i
            /
            (number_of_points - 1)
        )

        try:

            y = evaluate_function(
                function_string,
                x
            )

            if math.isfinite(y):

                x_values.append(x)

                y_values.append(y)

        except Exception:

            continue

    return {

        "x": x_values,

        "y": y_values

    }


class handler(BaseHTTPRequestHandler):


    def do_GET(self):

        try:

            parsed_url = urllib.parse.urlparse(
                self.path
            )

            query = urllib.parse.parse_qs(
                parsed_url.query
            )

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


            if start >= end:

                raise ValueError(
                    "Start of interval must be less than end."
                )


            if tolerance <= 0:

                raise ValueError(
                    "Tolerance must be greater than zero."
                )


            # Golden Section Search

            result = golden_section_search(
                function_string,
                start,
                end,
                tolerance
            )


            # Graph data

            graph = generate_graph_data(
                function_string,
                start,
                end
            )


            # Combine everything

            result["graph"] = graph


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
