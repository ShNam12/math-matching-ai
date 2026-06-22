import sympy as sp

from modules.neuro_symbolic.schemas import SolverDefinition, SolverOutput

CALCULUS_1_SOLVER_CODES = {
    "LIMIT_ZERO_ZERO",
    "DERIV_MONOMIAL",
    "DERIV_COMPOSITE",
    "INT_MONOMIAL",
    "INT_XN_EXP",
    "INT_XN_LN",
    "INT_RATIONAL",
}

class SolverNotFoundError(ValueError):
    pass


def _format_polynomial_term(coefficient: int, power: int) -> str:
    if power == 0:
        return str(coefficient)

    if power == 1:
        return f"{coefficient}x"

    return f"{coefficient}x^{power}"


def _format_integral_answer(coefficient: int, power: int) -> str:
    denominator = power + 1

    if coefficient == denominator:
        return f"x^{denominator} + C"

    if denominator == 1:
        return f"{coefficient}x + C"

    return f"{coefficient}/{denominator} x^{denominator} + C"


def solve_int_monomial(params: dict[str, object]) -> SolverOutput:
    coefficient = int(params.get("coefficient", 1))
    power = int(params.get("power", 1))

    if power == -1:
        raise ValueError("power=-1 is not supported by INT_MONOMIAL")

    integrand = _format_polynomial_term(coefficient, power)
    answer = _format_integral_answer(coefficient, power)

    return SolverOutput(
        statement=f"Tinh tich phan bat dinh $\\int {integrand}\\,dx$.",
        solution=(
            f"Ap dung cong thuc \\int ax^n dx = "
            f"a x^(n+1)/(n+1) + C voi n != -1. Ket qua la {answer}."
        ),
        answer=answer,
        answer_latex=answer,
        metadata={
            "coefficient": coefficient,
            "power": power,
        },
    )


def solve_derivative_monomial(params: dict[str, object]) -> SolverOutput:
    coefficient = int(params.get("coefficient", 1))
    power = int(params.get("power", 1))
    derivative_coefficient = coefficient * power
    derivative_power = power - 1
    expression = _format_polynomial_term(coefficient, power)
    answer = _format_polynomial_term(derivative_coefficient, derivative_power)

    return SolverOutput(
        statement=f"Tinh dao ham cua ham so $y={expression}$.",
        solution=(
            "Ap dung cong thuc (ax^n)' = anx^(n-1). "
            f"Ket qua la {answer}."
        ),
        answer=answer,
        answer_latex=answer,
        metadata={
            "coefficient": coefficient,
            "power": power,
        },
    )


def _int_param(params: dict[str, object], key: str, default: int) -> int:
    return int(params.get(key, default))


def _str_param(params: dict[str, object], key: str, default: str) -> str:
    return str(params.get(key, default))


def _sympy_output(
    *,
    statement: str,
    solution: str,
    result,
    metadata: dict[str, object],
) -> SolverOutput:
    simplified = sp.simplify(result)

    return SolverOutput(
        statement=statement,
        solution=solution,
        answer=str(simplified),
        answer_latex=sp.latex(simplified),
        metadata=metadata,
    )


def solve_int_xn_exp(params: dict[str, object]) -> SolverOutput:
    x = sp.symbols("x")
    n = _int_param(params, "n", 1)
    a = _int_param(params, "a", 1)
    lower = _int_param(params, "lower", 0)
    upper = _int_param(params, "upper", 1)
    integrand = x**n * sp.exp(a * x)
    result = sp.integrate(integrand, (x, lower, upper))

    return _sympy_output(
        statement=(
            f"Tinh tich phan $\\int_{{{lower}}}^{{{upper}}} "
            f"x^{{{n}}}e^{{{a}x}}\\,dx$."
        ),
        solution=(
            "Su dung tich phan tung phan hoac SymPy de tinh "
            f"\\int x^{n}e^({a}x) dx tren [{lower}, {upper}]."
        ),
        result=result,
        metadata={"n": n, "a": a, "lower": lower, "upper": upper},
    )


def solve_int_xn_ln(params: dict[str, object]) -> SolverOutput:
    x = sp.symbols("x")
    n = _int_param(params, "n", 1)
    lower = _int_param(params, "lower", 1)
    upper = params.get("upper", 2)
    integrand = x**n * sp.log(x)

    if upper is None:
        result = sp.integrate(integrand, x)
        bounds_text = ""
    else:
        upper_int = int(upper)
        result = sp.integrate(integrand, (x, lower, upper_int))
        bounds_text = f"_{{{lower}}}^{{{upper_int}}}"
        upper = upper_int

    return _sympy_output(
        statement=f"Tinh tich phan $\\int{bounds_text} x^{{{n}}}\\ln(x)\\,dx$.",
        solution="Su dung tich phan tung phan cho x^n ln(x).",
        result=result,
        metadata={"n": n, "lower": lower, "upper": upper},
    )


def solve_int_rational(params: dict[str, object]) -> SolverOutput:
    x = sp.symbols("x")
    a = _int_param(params, "a", 1)
    b = _int_param(params, "b", 0)
    c = _int_param(params, "c", 1)
    d = _int_param(params, "d", 1)
    lower = _int_param(params, "lower", 0)
    upper = params.get("upper", 1)
    integrand = (a * x + b) / (c * x + d)

    if upper is None:
        result = sp.integrate(integrand, x)
        bounds_text = ""
    else:
        upper_int = int(upper)
        result = sp.integrate(integrand, (x, lower, upper_int))
        bounds_text = f"_{{{lower}}}^{{{upper_int}}}"
        upper = upper_int

    return _sympy_output(
        statement=(
            f"Tinh tich phan $\\int{bounds_text} "
            f"\\frac{{{a}x+{b}}}{{{c}x+{d}}}\\,dx$."
        ),
        solution="Phan tich ham huu ti roi tinh tich phan.",
        result=result,
        metadata={
            "a": a,
            "b": b,
            "c": c,
            "d": d,
            "lower": lower,
            "upper": upper,
        },
    )


def solve_det_2x2(params: dict[str, object]) -> SolverOutput:
    a11 = _int_param(params, "a11", 1)
    a12 = _int_param(params, "a12", 0)
    a21 = _int_param(params, "a21", 0)
    a22 = _int_param(params, "a22", 1)
    matrix = sp.Matrix([[a11, a12], [a21, a22]])

    return _sympy_output(
        statement=(
            "Tinh dinh thuc $D = "
            f"\\begin{{vmatrix}} {a11} & {a12} \\\\ {a21} & {a22} "
            "\\end{vmatrix}$."
        ),
        solution="Dung cong thuc det = a11*a22 - a12*a21.",
        result=matrix.det(),
        metadata={"matrix": [[a11, a12], [a21, a22]]},
    )


def solve_det_3x3(params: dict[str, object]) -> SolverOutput:
    values = {
        key: _int_param(params, key, default)
        for key, default in {
            "a11": 1,
            "a12": 0,
            "a13": 0,
            "a21": 0,
            "a22": 1,
            "a23": 0,
            "a31": 0,
            "a32": 0,
            "a33": 1,
        }.items()
    }
    matrix = sp.Matrix(
        [
            [values["a11"], values["a12"], values["a13"]],
            [values["a21"], values["a22"], values["a23"]],
            [values["a31"], values["a32"], values["a33"]],
        ]
    )

    return _sympy_output(
        statement=(
            "Tinh dinh thuc ma tran 3x3 "
            f"$\\begin{{vmatrix}} {values['a11']} & {values['a12']} & {values['a13']} "
            f"\\\\ {values['a21']} & {values['a22']} & {values['a23']} "
            f"\\\\ {values['a31']} & {values['a32']} & {values['a33']} "
            "\\end{vmatrix}$."
        ),
        solution="Dung khai trien dinh thuc hoac bien doi hang.",
        result=matrix.det(),
        metadata={"matrix": matrix.tolist()},
    )


def solve_limit_zero_zero(params: dict[str, object]) -> SolverOutput:
    x = sp.symbols("x")
    numer_type = _str_param(params, "numer_type", "sin_x")
    denom_type = _str_param(params, "denom_type", "x")
    a = _int_param(params, "a", 1)
    b = _int_param(params, "b", 1)
    approach = _int_param(params, "approach", 0)

    numerators = {
        "sin_x": sp.sin(a * x),
        "tan_x": sp.tan(a * x),
        "exp_minus_1": sp.exp(a * x) - 1,
        "ln_1_plus_x": sp.log(1 + a * x),
        "poly": a * x + b * x**2,
    }
    denominators = {
        "x": b * x,
        "sin_x": sp.sin(b * x),
        "tan_x": sp.tan(b * x),
        "poly": b * x,
    }

    numerator_texts = {
        "sin_x": f"\\sin({a}x)",
        "tan_x": f"\\tan({a}x)",
        "exp_minus_1": f"e^{{{a}x}}-1",
        "ln_1_plus_x": f"\\ln(1+{a}x)",
        "poly": f"{a}x+{b}x^2",
    }
    denominator_texts = {
        "x": f"{b}x",
        "sin_x": f"\\sin({b}x)",
        "tan_x": f"\\tan({b}x)",
        "poly": f"{b}x",
    }

    numerator = numerators.get(numer_type, x)
    denominator = denominators.get(denom_type, x)
    numerator_text = numerator_texts.get(numer_type, "x")
    denominator_text = denominator_texts.get(denom_type, "x")

    result = sp.limit(numerator / denominator, x, approach)

    return _sympy_output(
        statement=(
            f"Tinh gioi han $\\lim_{{x\\to {approach}}} "
            f"\\frac{{{numerator_text}}}{{{denominator_text}}}$."
        ),
        solution=(
            "Rut gon bieu thuc hoac su dung cac gioi han co ban de tinh "
            "gioi han dang vo dinh."
        ),
        result=result,
        metadata={
            "numer_type": numer_type,
            "denom_type": denom_type,
            "a": a,
            "b": b,
            "approach": approach,
        },
    )
def solve_deriv_composite(params: dict[str, object]) -> SolverOutput:
    x = sp.symbols("x")
    f_type = _str_param(params, "f_type", "exp")
    g_type = _str_param(params, "g_type", "linear")
    a = _int_param(params, "a", 1)
    b = _int_param(params, "b", 0)
    point = params.get("point")

    if g_type == "linear":
        g = a * x + b
    elif g_type == "quadratic":
        g = a * x**2 + b
    elif g_type == "trig":
        g = sp.sin(a * x)
    else:
        g = x

    functions = {
        "exp": sp.exp(g),
        "sin": sp.sin(g),
        "cos": sp.cos(g),
        "ln": sp.log(g),
        "sqrt": sp.sqrt(g),
        "square": g**2,
    }
    expression = functions.get(f_type, g)
    result = sp.diff(expression, x)
    expression_latex = sp.latex(expression)

    if point is not None:
        result = result.subs(x, int(point))

    return _sympy_output(
        statement=f"Tinh dao ham cua ham so $y={expression_latex}$.",
        solution="Ap dung quy tac day chuyen: (f(g(x)))' = f'(g(x))*g'(x).",
        result=result,
        metadata={
            "f_type": f_type,
            "g_type": g_type,
            "a": a,
            "b": b,
            "point": point,
        },
    )


def _object_schema(properties: dict[str, object]) -> dict[str, object]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties.keys()),
    }


BUILTIN_SOLVERS: tuple[SolverDefinition, ...] = (
    SolverDefinition(
        code="INT_XN_EXP",
        name="Integral of x^n exp(a x)",
        taxonomy_hint="calculus.integration.by_parts.exp",
        param_schema=_object_schema(
            {
                "n": {"type": "integer", "minimum": 1, "maximum": 4},
                "a": {"type": "integer", "minimum": -5, "maximum": 5, "not": 0},
                "lower": {"type": "integer", "default": 0},
                "upper": {"type": "integer", "default": 1},
            }
        ),
        statement_template="Tinh $\\int_{lower}^{upper} x^{n}e^{a x}\\,dx$.",
        solution_template="Use integration by parts or symbolic integration.",
        answer_expression="integrate(x**n * exp(a*x), (x, lower, upper))",
        test_cases=[
            {
                "input": {"n": 2, "a": 3, "lower": 0, "upper": 1},
                "expected": "-2/27 + 5*exp(3)/27",
            },
            {
                "input": {"n": 1, "a": 1, "lower": 0, "upper": 1},
                "expected": "1",
            },
        ],
        solve=solve_int_xn_exp,
    ),
    SolverDefinition(
        code="INT_XN_LN",
        name="Integral of x^n ln(x)",
        taxonomy_hint="calculus.integration.by_parts.log",
        param_schema=_object_schema(
            {
                "n": {"type": "integer", "minimum": 0, "maximum": 4},
                "lower": {"type": "integer", "default": 1},
                "upper": {"type": "integer", "default": 2},
            }
        ),
        statement_template="Tinh $\\int_{lower}^{upper} x^{n}\\ln(x)\\,dx$.",
        solution_template="Use integration by parts.",
        answer_expression="integrate(x**n * log(x), (x, lower, upper))",
        test_cases=[
            {
                "input": {"n": 1, "lower": 1, "upper": 2},
                "expected": "-3/4 + 2*log(2)",
            },
            {
                "input": {"n": 2, "lower": 1, "upper": 2},
                "expected": "-7/9 + 8*log(2)/3",
            },
        ],
        solve=solve_int_xn_ln,
    ),
    SolverDefinition(
        code="INT_RATIONAL",
        name="Integral of rational linear quotient",
        taxonomy_hint="calculus.integration.rational",
        param_schema=_object_schema(
            {
                "a": {"type": "integer", "minimum": 1, "maximum": 3},
                "b": {"type": "integer", "minimum": -2, "maximum": 2},
                "c": {"type": "integer", "minimum": 1, "maximum": 3},
                "d": {"type": "integer", "minimum": 1, "maximum": 5},
                "lower": {"type": "integer", "default": 0},
                "upper": {"type": "integer", "default": 1},
            }
        ),
        statement_template="Tinh $\\int_{lower}^{upper} (a x+b)/(c x+d)\\,dx$.",
        solution_template="Integrate the rational expression symbolically.",
        answer_expression="integrate((a*x+b)/(c*x+d), (x, lower, upper))",
        test_cases=[
            {
                "input": {"a": 1, "b": 0, "c": 1, "d": 1, "lower": 0, "upper": 1},
                "expected": "1 - log(2)",
            },
            {
                "input": {"a": 2, "b": 1, "c": 1, "d": 2, "lower": 0, "upper": 1},
                "expected": "2 + 3*log(2) - 3*log(3)",
            },
        ],
        solve=solve_int_rational,
    ),
    SolverDefinition(
        code="DET_2X2",
        name="Determinant of a 2x2 matrix",
        taxonomy_hint="linear_algebra.determinant.2x2",
        param_schema=_object_schema(
            {
                "a11": {"type": "integer"},
                "a12": {"type": "integer"},
                "a21": {"type": "integer"},
                "a22": {"type": "integer"},
            }
        ),
        statement_template="Tinh dinh thuc ma tran 2x2.",
        solution_template="Use a11*a22 - a12*a21.",
        answer_expression="Matrix([[a11,a12],[a21,a22]]).det()",
        test_cases=[
            {
                "input": {"a11": 1, "a12": 2, "a21": 3, "a22": 4},
                "expected": "-2",
            },
            {
                "input": {"a11": 2, "a12": -1, "a21": 5, "a22": 3},
                "expected": "11",
            },
        ],
        solve=solve_det_2x2,
    ),
    SolverDefinition(
        code="DET_3X3",
        name="Determinant of a 3x3 matrix",
        taxonomy_hint="linear_algebra.determinant.3x3",
        param_schema=_object_schema(
            {
                "a11": {"type": "integer"},
                "a12": {"type": "integer"},
                "a13": {"type": "integer"},
                "a21": {"type": "integer"},
                "a22": {"type": "integer"},
                "a23": {"type": "integer"},
                "a31": {"type": "integer"},
                "a32": {"type": "integer"},
                "a33": {"type": "integer"},
            }
        ),
        statement_template="Tinh dinh thuc ma tran 3x3.",
        solution_template="Use determinant expansion or row operations.",
        answer_expression="Matrix(3x3).det()",
        test_cases=[
            {
                "input": {
                    "a11": 1,
                    "a12": 2,
                    "a13": 3,
                    "a21": 0,
                    "a22": 1,
                    "a23": 4,
                    "a31": 5,
                    "a32": 6,
                    "a33": 0,
                },
                "expected": "1",
            },
            {
                "input": {
                    "a11": 2,
                    "a12": 0,
                    "a13": 1,
                    "a21": 3,
                    "a22": 0,
                    "a23": 0,
                    "a31": 5,
                    "a32": 1,
                    "a33": 1,
                },
                "expected": "3",
            },
        ],
        solve=solve_det_3x3,
    ),
    SolverDefinition(
        code="LIMIT_ZERO_ZERO",
        name="Limit of an indeterminate 0/0 form",
        taxonomy_hint="calculus.limit.zero_zero",
        param_schema=_object_schema(
            {
                "numer_type": {
                    "type": "string",
                    "enum": [
                        "sin_x",
                        "tan_x",
                        "exp_minus_1",
                        "ln_1_plus_x",
                        "poly",
                    ],
                },
                "denom_type": {
                    "type": "string",
                    "enum": ["x", "sin_x", "tan_x", "poly"],
                },
                "a": {"type": "integer", "minimum": 1, "maximum": 5},
                "b": {"type": "integer", "minimum": 1, "maximum": 5},
                "approach": {"type": "integer", "default": 0},
            }
        ),
        statement_template="Tinh gioi han dang 0/0.",
        solution_template="Use standard limits or L'Hopital.",
        answer_expression="limit(numerator/denominator, x, approach)",
        test_cases=[
            {
                "input": {"numer_type": "sin_x", "denom_type": "x", "a": 3, "b": 2},
                "expected": "3/2",
            },
            {
                "input": {
                    "numer_type": "exp_minus_1",
                    "denom_type": "x",
                    "a": 4,
                    "b": 2,
                },
                "expected": "2",
            },
        ],
        solve=solve_limit_zero_zero,
    ),
    SolverDefinition(
        code="DERIV_COMPOSITE",
        name="Derivative of a composite function",
        taxonomy_hint="calculus.derivative.chain_rule",
        param_schema=_object_schema(
            {
                "f_type": {
                    "type": "string",
                    "enum": ["exp", "sin", "cos", "square"],
                },
                "g_type": {
                    "type": "string",
                    "enum": ["linear", "quadratic", "trig"],
                },
                "a": {"type": "integer", "minimum": 1, "maximum": 5},
                "b": {"type": "integer", "minimum": -5, "maximum": 5},
            }
        ),
        statement_template="Tinh dao ham ham hop f(g(x)).",
        solution_template="Use the chain rule.",
        answer_expression="diff(f(g(x)), x)",
        test_cases=[
            {
                "input": {"f_type": "exp", "g_type": "linear", "a": 2, "b": 1},
                "expected": "2*exp(2*x + 1)",
            },
            {
                "input": {"f_type": "square", "g_type": "quadratic", "a": 2, "b": 3},
                "expected": "8*x*(2*x**2 + 3)",
            },
        ],
        solve=solve_deriv_composite,
    ),
    SolverDefinition(
        code="INT_MONOMIAL",
        name="Indefinite integral of a monomial",
        taxonomy_hint="calculus.integration.monomial",
        param_schema={
            "type": "object",
            "properties": {
                "coefficient": {"type": "integer", "default": 1},
                "power": {"type": "integer", "default": 1},
            },
            "required": ["coefficient", "power"],
        },
        statement_template="Tinh tich phan bat dinh $\\int {coefficient}x^{power}\\,dx$.",
        solution_template="Use the power rule for indefinite integrals.",
        answer_expression="{coefficient}/{power_plus_one} x^{power_plus_one} + C",
        solve=solve_int_monomial,
    ),
    SolverDefinition(
        code="DERIV_MONOMIAL",
        name="Derivative of a monomial",
        taxonomy_hint="calculus.derivative.monomial",
        param_schema={
            "type": "object",
            "properties": {
                "coefficient": {"type": "integer", "default": 1},
                "power": {"type": "integer", "default": 1},
            },
            "required": ["coefficient", "power"],
        },
        statement_template="Tinh dao ham cua ham so $y={coefficient}x^{power}$.",
        solution_template="Use the power rule for derivatives.",
        answer_expression="{coefficient}*{power} x^{power_minus_one}",
        solve=solve_derivative_monomial,
    ),
)


class SolverRegistry:
    def __init__(
        self,
        solvers: list[SolverDefinition] | tuple[SolverDefinition, ...] | None = None,
    ) -> None:
        self._solvers: dict[str, SolverDefinition] = {}

        for solver in solvers or BUILTIN_SOLVERS:
            self.register(solver)

    def register(self, solver: SolverDefinition) -> None:
        if solver.code in self._solvers:
            raise ValueError(f"Duplicate solver code: {solver.code}")

        self._solvers[solver.code] = solver

    def list_solvers(self) -> list[SolverDefinition]:
        return [
            self._solvers[code]
            for code in sorted(self._solvers)
        ]

    def get_solver(self, code: str) -> SolverDefinition:
        normalized_code = code.strip().upper()

        try:
            return self._solvers[normalized_code]
        except KeyError as exc:
            raise SolverNotFoundError(
                f"Solver not found: {normalized_code}"
            ) from exc
