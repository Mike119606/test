# -*- coding: utf-8 -*-
"""Generate the Word document: 高数课件英文词汇+题目+答案"""
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

# ---- set default font to support Chinese ----
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

def set_run_font(run, name_en='Times New Roman', name_zh='宋体', size=11, bold=False, color=None):
    run.font.name = name_en
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name_zh)
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_title(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    set_run_font(r, name_zh='黑体', size=20, bold=True)
    return p

def add_h1(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_run_font(r, name_zh='黑体', size=16, bold=True, color=(31, 73, 125))
    return p

def add_h2(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_run_font(r, name_zh='黑体', size=13, bold=True, color=(47, 84, 150))
    return p

def add_para(text, size=11, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_run_font(r, size=size, bold=bold)
    return p

# ============================================================
# 封面标题
# ============================================================
add_title('高等数学课件整理')
sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run('英文数学词汇 / 例题与习题 / 参考答案\n（基于五份英文课件整理）')
set_run_font(r, name_zh='楷体', size=12)
doc.add_paragraph()

# ============================================================
# 第一部分：数学相关英文词汇（去重 + 中文注释）
# ============================================================
add_h1('第一部分  数学相关英文词汇表')
add_para('说明：以下词汇从五份课件中提取，去重后按主题分类，并给出中文注释。', size=10)

vocab = [
    # ---- 数与集合 ----
    ('数系与集合', [
        ('natural number', '自然数'),
        ('integer', '整数'),
        ('rational number', '有理数'),
        ('real number', '实数'),
        ('complex number', '复数'),
        ('imaginary unit', '虚数单位 (i)'),
        ('real part / imaginary part', '实部 / 虚部 (Re / Im)'),
        ('conjugate', '共轭复数'),
        ('modulus (absolute value)', '模（绝对值）'),
        ('argument', '辐角'),
        ('principal value (principal determination)', '主值'),
        ('Cartesian (binomial) form', '笛卡尔（代数）形式'),
        ('polar form', '极坐标形式'),
        ('trigonometric form', '三角形式'),
        ('exponential form', '指数形式'),
        ('Affix', '（复数在复平面上的）点'),
        ('complex plane (Argand diagram)', '复平面（阿甘德图）'),
        ('real axis / imaginary axis', '实轴 / 虚轴'),
        ('n-th root', 'n 次方根'),
        ('regular polygon', '正多边形'),
        ('De Moivre\'s formula', '棣莫弗公式'),
        ('Euler\'s formula', '欧拉公式 e^(iα)=cosα+i sinα'),
        ('complex exponential', '复指数函数'),
        ('complex logarithm', '复对数'),
        ('Fundamental Theorem of Algebra', '代数基本定理'),
        ('induction', '数学归纳法'),
        ('binomial theorem', '二项式定理'),
        ('supremum (least upper bound)', '上确界'),
        ('infimum (greatest lower bound)', '下确界'),
        ('maximum / minimum', '最大值 / 最小值'),
        ('upper bound / lower bound', '上界 / 下界'),
        ('completeness axiom', '完备性公理'),
        ('bounded above / below', '有上界 / 有下界'),
        ('well ordered', '良序的'),
        ('dense', '稠密的'),
        ('irrational', '无理的'),
        ('decimal expansion', '十进制展开'),
        ('eventually periodic', '最终周期的'),
        ('interval', '区间'),
        ('absolute value', '绝对值'),
        ('triangle inequality', '三角不等式'),
    ]),
    # ---- 函数 ----
    ('函数基本概念', [
        ('function', '函数'),
        ('domain', '定义域'),
        ('range (image)', '值域'),
        ('graph', '图像'),
        ('injective (one-to-one)', '单射的'),
        ('even / odd function', '偶函数 / 奇函数'),
        ('monotone (monotonic)', '单调的'),
        ('increasing / decreasing', '递增 / 递减'),
        ('bounded / periodic', '有界的 / 周期的'),
        ('inverse function', '反函数'),
        ('composite function', '复合函数'),
        ('elementary function', '初等函数'),
        ('exponential function', '指数函数'),
        ('natural (Napierian) logarithm', '自然对数'),
        ('decimal logarithm', '常用对数（以10为底）'),
        ('change of base', '换底公式'),
        ('transcendental number', '超越数'),
        ('trigonometric function', '三角函数'),
        ('sine / cosine / tangent', '正弦 / 余弦 / 正切'),
        ('cotangent / secant / cosecant', '余切 / 正割 / 余割'),
        ('inverse trigonometric function', '反三角函数'),
        ('arcsin / arccos / arctan', '反正弦 / 反余弦 / 反正切'),
        ('hyperbolic function', '双曲函数'),
        ('hyperbolic sine (sh/sinh)', '双曲正弦'),
        ('hyperbolic cosine (ch/cosh)', '双曲余弦'),
        ('hyperbolic tangent (th/tanh)', '双曲正切'),
        ('hyperbolic cosecant (csch)', '双曲余割'),
        ('hyperbolic secant (sech)', '双曲正割'),
        ('hyperbolic cotangent (coth)', '双曲余切'),
        ('inverse hyperbolic function (argsh, argch, ...)', '反双曲函数'),
    ]),
    # ---- 数列与极限 ----
    ('数列与极限', [
        ('sequence', '数列'),
        ('general term', '通项'),
        ('convergence / convergent', '收敛 / 收敛的'),
        ('divergence / divergent', '发散 / 发散的'),
        ('limit', '极限'),
        ('unique limit', '极限的唯一性'),
        ('bounded sequence', '有界数列'),
        ('monotone convergence theorem', '单调收敛定理'),
        ('oscillating', '振荡的'),
        ('properly divergent', '正常发散（趋于±∞）'),
        ('indeterminate form', '未定式'),
        ('hierarchy of infinities', '无穷大的阶（增长速度比较）'),
        ('arithmetic sequence', '等差数列'),
        ('geometric sequence', '等比数列'),
        ('common difference / ratio', '公差 / 公比'),
        ('partial sum', '部分和'),
        ('neighbourhood', '邻域'),
        ('punctured neighbourhood', '去心邻域'),
        ('accumulation point', '聚点'),
        ('lateral (one-sided) limit', '单侧极限'),
        ('left-hand / right-hand limit', '左极限 / 右极限'),
        ('asymptote', '渐近线'),
        ('vertical / horizontal / oblique asymptote', '垂直 / 水平 / 斜渐近线'),
        ('remarkable limit', '重要极限'),
        ('equivalent infinitesimal', '等价无穷小'),
        ('squeeze (sandwich) rule', '夹逼准则'),
        ('sequential characterisation', '海涅归结原则（数列刻画）'),
    ]),
    # ---- 连续 ----
    ('连续性', [
        ('continuity / continuous', '连续性 / 连续的'),
        ('discontinuity / discontinuous', '间断 / 间断的'),
        ('removable discontinuity', '可去间断点'),
        ('jump discontinuity', '跳跃间断点'),
        ('infinite discontinuity', '无穷间断点'),
        ('essential discontinuity', '本质（第二类）间断点'),
        ('Bolzano\'s theorem', '波尔查诺定理（零点存在定理）'),
        ('bisection method', '二分法'),
        ('Darboux theorem (intermediate value theorem)', '达布定理（介值定理）'),
        ('Weierstrass theorem', '魏尔斯特拉斯定理（最值定理）'),
        ('fixed point', '不动点'),
        ('closed and bounded interval', '闭且有界的区间'),
    ]),
    # ---- 微分 ----
    ('微分学', [
        ('derivative', '导数'),
        ('differentiable / differentiability', '可微的 / 可微性'),
        ('difference quotient', '差商'),
        ('secant line', '割线'),
        ('tangent line', '切线'),
        ('normal line', '法线'),
        ('lateral derivative', '单侧导数'),
        ('rate of change', '变化率'),
        ('instantaneous velocity', '瞬时速度'),
        ('chain rule', '链式法则'),
        ('implicit differentiation', '隐函数求导'),
        ('logarithmic differentiation', '对数求导法'),
        ('differential', '微分'),
        ('linear approximation', '线性近似'),
        ('propagation of errors', '误差传播'),
        ('relative error', '相对误差'),
        ('extremum (pl. extrema)', '极值'),
        ('global / local extremum', '全局 / 局部极值'),
        ('critical point', '临界点（驻点或不可导点）'),
        ('Fermat\'s theorem', '费马定理'),
        ('Rolle\'s theorem', '罗尔定理'),
        ('Lagrange\'s theorem (mean value theorem)', '拉格朗日中值定理'),
        ('Cauchy\'s theorem', '柯西中值定理'),
        ('monotonicity (from sign of f\')', '（由导数符号判断的）单调性'),
        ('concavity', '凹凸性'),
        ('concave up / down', '上凹（下凸）/ 下凹（上凸）'),
        ('inflection point', '拐点'),
        ('second derivative criterion', '二阶导数判别法'),
        ('L\'Hôpital\'s rule', '洛必达法则'),
        ('optimization', '最优化'),
        ('Taylor polynomial', '泰勒多项式'),
        ('Maclaurin polynomial', '麦克劳林多项式（x₀=0的泰勒多项式）'),
        ('Taylor\'s theorem', '泰勒定理'),
        ('Lagrange remainder', '拉格朗日余项'),
        ('order (of a polynomial/derivative)', '阶'),
        ('small-angle approximation', '小角度近似'),
        ('first non-vanishing derivative', '首个非零导数'),
    ]),
    # ---- 积分 ----
    ('积分学', [
        ('primitive (antiderivative)', '原函数（不定积分的被积函数的逆运算结果）'),
        ('indefinite integral', '不定积分'),
        ('integrand', '被积函数'),
        ('constant of integration', '积分常数'),
        ('immediate integral', '直接（基本）积分'),
        ('integration by parts', '分部积分法'),
        ('change of variable (substitution)', '换元积分法'),
        ('direct substitution', '直接换元'),
        ('inverse substitution', '三角换元（逆代换）'),
        ('rational function', '有理函数'),
        ('partial fractions', '部分分式分解'),
        ('reduction formula', '递推公式（降阶公式）'),
        ('Riemann integral', '黎曼积分'),
        ('Riemann sum', '黎曼和'),
        ('Darboux sum (upper/lower sum)', '达布和（上和 / 下和）'),
        ('partition', '分割'),
        ('norm of a partition', '分割的细度（模）'),
        ('definite integral', '定积分'),
        ('integrable', '可积的'),
        ('piecewise continuous', '分段连续的'),
        ('uniform continuity', '一致连续'),
        ('Heine-Cantor theorem', '海涅-康托尔定理'),
        ('Riemann\'s criterion', '黎曼可积准则'),
        ('mean value theorem for integrals', '积分中值定理'),
        ('average value', '平均值'),
        ('fundamental theorem of calculus', '微积分基本定理'),
        ('Barrow\'s rule', '巴罗法则（牛顿-莱布尼茨公式）'),
        ('area', '面积'),
        ('volume of revolution', '旋转体体积'),
        ('disc method', '圆盘法'),
        ('washer method', '圆环（垫圈）法'),
        ('cylindrical shells method', '柱壳法'),
        ('annulus', '圆环'),
        ('torus', '圆环面（轮胎体）'),
        ('arc length', '弧长'),
        ('element of arc (ds)', '弧微分'),
    ]),
    # ---- 级数 ----
    ('级数', [
        ('series', '级数'),
        ('terms of the series', '级数的项'),
        ('convergent / divergent series', '收敛 / 发散级数'),
        ('sum of a series', '级数的和'),
        ('properly divergent', '正常发散'),
        ('finitely oscillating', '有限振荡'),
        ('infinitely oscillating', '无限振荡'),
        ('necessary condition for convergence', '收敛的必要条件'),
        ('divergence test', '发散判别法'),
        ('harmonic series', '调和级数'),
        ('geometric series', '几何级数（等比级数）'),
        ('telescopic (telescoping) series', '望远镜级数（裂项相消）'),
        ('p-series (generalized harmonic series)', 'p 级数（广义调和级数）'),
        ('comparison test (direct)', '比较判别法'),
        ('limit comparison test', '极限比较判别法'),
        ('D\'Alembert\'s test (ratio test)', '达朗贝尔判别法（比值判别法）'),
        ('Cauchy\'s test (root test)', '柯西判别法（根值判别法）'),
        ('Raabe\'s test', '拉阿伯判别法'),
        ('integral test', '积分判别法'),
        ('alternating series', '交错级数'),
        ('Leibniz\'s test', '莱布尼茨判别法'),
        ('absolute convergence', '绝对收敛'),
        ('conditional convergence', '条件收敛'),
        ('unconditional convergence', '无条件收敛'),
        ('rearrangement', '重排'),
        ('Riemann\'s rearrangement theorem', '黎曼重排定理'),
        ('functional sequence', '函数列'),
        ('pointwise convergence', '逐点收敛'),
        ('uniform convergence', '一致收敛'),
        ('supremum criterion', '上确界判别法'),
        ('Dini\'s theorem', '迪尼定理'),
        ('Weierstrass M-test', '魏尔斯特拉斯 M 判别法'),
        ('functional series', '函数项级数'),
        ('field (domain) of convergence', '收敛域'),
        ('power series', '幂级数'),
        ('radius of convergence', '收敛半径'),
        ('centre of a power series', '幂级数的中心'),
        ('Abel\'s lemma', '阿贝尔引理'),
        ('Taylor expansion', '泰勒展开'),
        ('analytic function', '解析函数'),
        ('Cauchy product', '柯西乘积'),
        ('term-by-term differentiation/integration', '逐项微分 / 逐项积分'),
    ]),
]

for topic, words in vocab:
    add_h2(topic)
    for en, zh in words:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Pt(18)
        r1 = p.add_run(en + '  ')
        set_run_font(r1, size=11, bold=True)
        r2 = p.add_run('—  ' + zh)
        set_run_font(r2, size=11)

doc.add_page_break()

# ============================================================
# 第二部分：例题 (Examples) 与 习题 (Exercises)
# ============================================================
add_h1('第二部分  例题与习题（原题，不翻译）')
add_para('说明：以下列出课件中的 Example（例题）与 Exercise（习题）。题目按课件主题分组；答案统一在第三部分给出。', size=10)

# ---------- Topic 2 ----------
add_h2('Topic 2 — Sequences and Limits（数列与极限）')
add_para('Examples', size=12, bold=True)
examples_t2 = [
    'Monotonicity and bounds. aₙ = n/(n+1): show it is strictly increasing and bounded.',
    'Using the definition. Prove that lim_{n→∞} (2n+1)/(n+3) = 2.',
    'Monotone convergence. aₙ = (1+1/n)ⁿ is increasing and bounded above by 3; find its limit.',
    'Arithmetic sequence. a₁ = 5, d = 3: find a₂₀ and S₂₀.',
    'Two examples (why |r|<1 matters). (a) Sum 2 + 2/3 + 2/9 + ... ; (b) Show 0.9̄ = 1.',
    'Two examples (function limits). (a) From the definition: lim_{x→3}(2x−1) = 5. (b) lim_{x→1}(x²−1)/(x−1).',
    'Sequential characterisation. Show lim_{x→0} sin(1/x) does not exist.',
    'Lateral limits. (a) f(x)=|x|/x at x=0; (b) find k so that lim_{x→2} f(x) exists for f(x)=x²+1 (x<2), k−x (x≥2).',
    'Squeeze rule. lim_{x→0} x·sin(1/x).',
    'Asymptotes. f(x)=(2x²+3)/(x−1): find all asymptotes.',
    'Three computations (remarkable limits): (a) sin3x/(5x); (b) (1−cosx)/(x sinx); (c) (1+3/x)^{2x}.',
    'Classification of discontinuities: one example of each (removable, jump, infinite, essential).',
    'Bisection method. x³+x−1=0 on [0,1]: locate the root and justify uniqueness.',
    'Fixed point. If f:[0,1]→[0,1] is continuous, prove f(c)=c for some c.',
]
for i, q in enumerate(examples_t2, 1):
    add_para(f'Example {i}. {q}')

add_para('Exercises', size=12, bold=True)
ex_t2 = [
    'Compute (a) lim_{n→∞}(3n²−n+1)/(2n²+5); (b) lim_{n→∞}(√(n²+n)−n); (c) lim_{n→∞}((n+2)/n)^{3n}.',
    '(a) In an arithmetic sequence a₃=11, a₈=26: find a₁, d, a₁₀, S₁₀. (b) Sum 6+2+2/3+2/9+...',
    'Let a₁=2, a_{n+1}=(aₙ+2/aₙ)/2. Prove aₙ≥√2, decreasing, convergent; compute the limit.',
    'Compute (a) lim_{x→2}(x²−4)/(x²−3x+2); (b) lim_{x→0}(√(1+x)−1)/x; (c) lim_{x→1}(x³−1)/(x²−1).',
    'Find a, b for which f is continuous on R, where f(x)=x+a (x<1), x² (1≤x<2), b−x (x≥2).',
    'Compute (a) lim_{x→0}(1−cosx)/(x tanx); (b) lim_{x→0}(e^{2x}−1)/ln(1+3x); (c) lim_{x→+∞}((x+1)/(x−2))^x.',
    'Classify the discontinuities of f(x)=(x²−x−6)/(x−3), g(x)=x/(x²−1), h(x)=e^{1/x}.',
    'Find the domain and all asymptotes of f(x)=x²/(x+1).',
    'Prove e^x = 3−x has at least one solution in ]0,1[, locate it in an interval of length 1/4, justify uniqueness.',
    '(a) Prove cos x = x has exactly one solution in [0,1]. (b) f(x)=x³−3x attains max and min on [0,2]; compute both.',
    'Using only definitions, prove (a) lim_{n→∞}(3n−1)/(n+2)=3; (b) lim_{x→2}(5x−3)=7; (c) lim_{n→∞}(2n²−1)=+∞. Give the smallest N for ε=10⁻³ in (a).',
    'Study monotonicity, bounds and behaviour of (a) aₙ=(3n−2)/(n+1); (b) aₙ=n/2ⁿ; (c) aₙ=(−1)ⁿ(n+1)/n.',
    'Using the hierarchy of infinities, compute (a) lim(2ⁿ+n⁵)/(n!+3ⁿ); (b) lim n³ ln n / 2ⁿ; (c) lim ((n+1)!−n!)/((n+1)!+n!).',
    'Compute by the squeeze rule (a) lim sin n / n; (b) lim Σ_{k=1}^n 1/(n²+k); (c) lim_{x→0} x² cos(1/x).',
    '(a) An echo loses 20% amplitude per reflection: x₁=5, x_{n+1}=0.8 xₙ. Write xₙ, decide stability, sum all amplitudes, find first n with xₙ<10⁻². (b) Bisection on [1,2]: steps for error <10⁻³ and <10⁻⁶?',
    'Decide whether limits exist (lateral limits or sequences): (a) lim_{x→2}|x−2|/(x²−4); (b) lim_{x→0}1/(1+e^{1/x}); (c) lim_{x→0}cos(1/x).',
    '(a) lim_{x→−∞}(√(x²+3x)+x). (b) Horizontal asymptotes of f(x)=(2x+1)/√(x²+1). (c) All asymptotes of g(x)=x e^{1/x}.',
    'Compute (a) lim_{x→π} sinx/(x−π); (b) lim_{x→1} ln x/(x²−1); (c) lim_{x→1}(1/(x−1)−3/(x³−1)); (d) lim_{x→+∞} x ln((x+1)/x).',
    '(a) Every odd-degree polynomial has a real root. (b) x⁵−3x+1=0 has at least three real solutions; locate each in an interval of length 1. (c) f(x)=x³+x²−1 takes value 5 in [0,2], only once.',
    'True or false, with proof or counterexample: (a) every bounded sequence converges; (b) if {|aₙ|} converges so does {aₙ}; (c) if lim_{x→a}f exists finite, f is continuous at a; (d) continuous on bounded interval ⇒ bounded; (e) f continuous on [a,b], f(a)f(b)>0 ⇒ f does not vanish on ]a,b[; (f) aₙ→L>0 ⇒ aₙ>0 from some index.',
]
for i, q in enumerate(ex_t2, 1):
    add_para(f'Exercise {i}. {q}')

# ---------- Topic 3 ----------
add_h2('Topic 3 — Differential Calculus（微分学）')
add_para('Examples', size=12, bold=True)
examples_t3 = [
    'Tangent and normal lines. f(x)=√x at x₀=4 (from the definition); write t and n.',
    'Lateral derivatives. f(x)=|x| at x₀=0: compute f\'(0+) and f\'(0−).',
    'Three derivatives: (a) y=ln√(1+x²); (b) y=arctan(e^{2x}); (c) y=x² sinx/(1+x).',
    'Logarithmic differentiation: y=xˣ. Implicit differentiation: x²+y²=25, find y\' at (3,4).',
    'Linear approximation: (a) √4.05; (b) square side 10 cm, error 0.02 cm — relative error of area.',
    'A complete example: study f(x)=x³−3x²−9x+5 (monotonicity, extrema, concavity, inflection).',
    'L\'Hôpital — three limits: (a) lim_{x→0}(eˣ−1−x)/x²; (b) lim_{x→+∞} ln x / x; (c) lim_{x→0+} x ln x (then lim xˣ).',
    'Optimization — open box: square sheet 12 cm, corner squares of side x; maximum volume.',
    'Optimization — most economical can: fixed volume V, minimize surface area.',
    'Taylor polynomial of sin x (P₁, P₃, P₅) at 0.',
    'Approximation with error: e^{0.1} with P₃; bound |R₃|; choose n for ε=10⁻⁸.',
    'Taylor of ln(1+x); of 1/(1−x); of cosh x.',
    'Substitution: f(x)=e^{−x²} — find P₄. Small-angle approximations.',
    'Limits via expansions: lim_{x→0}(x−sinx)/x³. General criterion for extrema (first non-vanishing derivative).',
]
for i, q in enumerate(examples_t3, 1):
    add_para(f'Example {i}. {q}')

add_para('Exercises', size=12, bold=True)
ex_t3 = [
    'From the definition, compute f\'(1) for f(x)=1/(x+1); write tangent and normal at that point.',
    'Find a, b so that f(x)=x² (x≤1), ax+b (x>1) is differentiable at x=1. Is it differentiable everywhere?',
    'Differentiate (a) y=ln√((1+x)/(1−x)); (b) y=arctan(e^{2x}); (c) y=x^{sin x} (x>0).',
    'Folium of Descartes x³+y³=6xy passes through (3,3). Compute y\' implicitly and write the tangent there.',
    '(a) Find c of Lagrange\'s theorem for f(x)=ln x on [1,e]. (b) Prove |sin a − sin b| ≤ |a − b|.',
    'Study monotonicity, local extrema, concavity and inflection points of f(x)=x³−3x²−9x+5.',
    'Find the global maximum and minimum of f(x)=x e^{−x} on [0,3].',
    'Rectangular field 1800 m² fenced on three sides (river along the fourth). Minimise the fence.',
    'Compute (a) lim_{x→0}(eˣ−1−x)/x²; (b) lim_{x→0}(x−sinx)/x³; (c) lim_{x→0+} xˣ.',
    'Maclaurin polynomial of order 3 of f(x)=√(1+x); approximate √1.1 and bound the error.',
    'Study continuity and differentiability of (a) f(x)=|x²−4| on R; (b) g(x)=∛x at x₀=0.',
    'Find a formula for the n-th derivative of (a) e^{−3x}; (b) 1/(1+x); (c) sin x.',
    '(a) Estimate ∛8.12 with the differential. (b) Sphere radius measured with 1% relative error — relative error of volume?',
    '(a) Verify Rolle\'s hypotheses for f(x)=x²−4x+3 on [1,3] and find c. (b) Prove x³+3x−1=0 has exactly one real root.',
    'Prove, studying an auxiliary function: (a) eˣ ≥ 1+x on R; (b) sin x < x for x>0.',
    'Find the point of the parabola y=x² closest to (3,0), and the distance.',
    'Compute (a) lim_{x→0}(1/x − 1/sin x); (b) lim_{x→0}(cos x)^{1/x²}.',
    'Using known expansions, obtain Maclaurin polynomial of (a) ln(1+2x) order 3; (b) 1/(1+x²) order 4; (c) sin(x²) order 6.',
    '(a) lim_{x→0}(cos x −1 + x²/2)/x⁴ (Taylor). (b) Classify x=0 for f(x)=cos x −1 + x²/2 and g(x)=sin x −x (first non-vanishing derivative).',
    '(a) Smallest n for Maclaurin of eˣ to give e^{0.5} with error <10⁻⁶; compute it. (b) Approximate sin(0.2) by P₃ and bound the error.',
]
for i, q in enumerate(ex_t3, 1):
    add_para(f'Exercise {i}. {q}')

# ---------- Basic Notions ----------
add_h2('Unit 1 — Basic Notions（基本概念：数系、函数、三角与双曲函数）')
add_para('Examples', size=12, bold=True)
examples_bn = [
    'A = {1 − 1/n}: find min, inf, sup, max.',
    'Sum, difference and product of z₁=(3,5) and z₂=(4,3) in Cartesian form.',
    'Example 1.2: same with binomial form. Example 1.3: roots of x²+x+1=0.',
    'Conjugate, modulus, distance: z₁=(3,5), z₂=(4,3).',
    'Example 1.4: quotient (3+5i)/(−2−3i).',
    'Example 2.1: modulus and argument of −1+i (principal value).',
    'Example 2.2: arg_{6π}(−1+i), arg_{7π}(−1+i), arg_{7π/4}(−1+i).',
    'Example 2.3: 2−2i, i, −1+√3 i in Cartesian, polar and trigonometric form.',
    'Example 3.1: express sin(3α) in terms of sin α, cos α (De Moivre).',
    'Example 4.1: square roots of i. Example 4.2: square roots of −1+√3 i. Example 4.3: solve z⁴−16=0.',
    'Example 5.1: e^{iπ/2}, e^{iπ}, e^{−iπ}, e^{3iπ/2}, e^{−iπ/2}, e^{2iπ}.',
    'Example 5.2: −1+i in exponential form; compute ln z. Example 5.3: 1/(1+i)⁸ in binomial form. Example 5.4: (1−i)^{2i}/(1+√3 i) in exponential form.',
    'Inverse function: check f(x)=5x³+2 and g(x)=∛((x−2)/5) are inverses; find inverse of f(x)=5x³+2.',
    'Derivative of inverse (Theorem 1.2.8) — check with Example 1.2.',
    'Immediate integrals (table) — Example 1.2: ∫(2x+3)/(x²+3x+7) dx, ∫x e^{x²} dx, ∫3x²(x²+1) dx.',
]
for i, q in enumerate(examples_bn, 1):
    add_para(f'Example {i}. {q}')

add_para('Exercises', size=12, bold=True)
ex_bn = [
    'Prove by induction: 1+3+5+...+(2n−1) = n².',
    '(a) Prove √3 is irrational. (b) Write x = 0.427̄ (period 27) as a quotient of two integers.',
    'Solve |x−2|≥5 and |3x+1|<2 in R; find sup, inf, max, min (if exist) of {2+(−1)ⁿ/n : n∈N*}.',
    'Express in binomial form z = (2+i)/(1−3i).',
    'Compute (1+√3 i)¹⁰.',
    'Solve z⁴+4=0 and describe the position of the four affixes.',
    'Express cos(3α) in terms of cos α alone.',
    'Compute all values of ln(−i) and its principal determination.',
    'Describe the set {z∈C : |z−1| = |z+i|}.',
    'Prove |z₁+z₂|²+|z₁−z₂|² = 2(|z₁|²+|z₂|²) for all z₁,z₂∈C; give the geometric meaning.',
    'Compute the six sixth roots of unity, draw their affixes; prove the sum of the n n-th roots of 1 is zero (n≥2).',
    'f(x)=ln((x−1)/(x+2)): find domain, prove injective, determine range, compute f⁻¹.',
    'Classify by parity, boundedness and periodicity: f(x)=x² cos x, g(x)=th x, h(x)=sin x+cos x; write e^{2x} as even + odd.',
    'Find the inverse (if it exists) of f(x)=2ˣ/(1+2ˣ), x∈]0,1[.',
    'Prove the change-of-base formula log_a x = log_b x / log_b a (a,b>0, ≠1); deduce the ln / log₁₀ relations.',
    'f(x)=x+ln x on ]0,+∞[: justify it has an inverse g on all R; compute g\'(1) without finding g.',
    'f(x)=(x−1)/(x+1): find domain; compute f∘f and f∘f∘f∘f; obtain f⁻¹.',
    '(a) Prove arcsin x + arccos x = π/2 on [−1,1]. (b) Simplify cos(arcsin x), tan(arcsin x). (c) Deduce derivative of arcsin.',
    'Prove the addition formulas for sh and ch; deduce sh 2x, ch 2x.',
    '(a) Prove argcoth x = argth(1/x); state valid x. (b) Solve ch x = 5/2 (find sh x, th x); solve ch x = a for arbitrary a≥1.',
]
for i, q in enumerate(ex_bn, 1):
    add_para(f'Exercise {i}. {q}')

# ---------- Integral Calculus ----------
add_h2('Unit 4 — Integral Calculus（积分学）')
add_para('Examples', size=12, bold=True)
examples_int = [
    'Example 1.1: verify F(x)=x sin x+cos x is a primitive of f(x)=x cos x on R.',
    'Example 1.2 (composite integrals): ∫(2x+3)/(x²+3x+7) dx, ∫x e^{x²} dx, ∫3x²(x²+1) dx.',
    'Example 1.3: ∫(x⁴−3x²+5) dx. Example 1.4: ∫tan²x dx. Example 1.5: ∫dx/(sin x cos x).',
    'Example 1.6: ∫√((1−x)/(1+x)) dx on ]−1,1[.',
    'Example 2.1: ∫sin(3x+5) cos(2x−3) dx (product-to-sum).',
    'Integration by parts: ∫x² eˣ dx on R.',
    'Example 3.1: ∫ln(1+x) dx on ]−1,+∞[. Example 3.2: ∫arcsin x dx on ]−1,1[.',
    'Example 3.3: compute ∫e^{ax}cos(bx) dx and ∫e^{ax}sin(bx) dx simultaneously.',
    'Example 3.4: compute ∫sin²x dx and ∫cos²x dx simultaneously.',
    'Example 3.5: reduction formula for Iₙ=∫xⁿ eˣ dx; compute I₃.',
    'Example 4.1: ∫√(4−x²) dx on ]−2,2[ (x=2 sin t). Example 4.2: ∫sin x ln(cos x) dx.',
    'Example 5.1: ∫(4x⁴+4x³+x²−7)/(2x+1) dx (polynomial division).',
    'Example 5.2: partial fractions — (a) ∫(x²+5x+7)/(x³+4x²−x−4) dx; (b) ∫(3x+4)/(2+3x−9x²) dx; (c) ∫dx/(x³−3x²+3x−1); (d) ∫x²/(x⁴+5x²+4) dx; (e) ∫(5x³−28x²+53x−21)/(x⁴−7x³+9x²+8x+16) dx.',
    'Example 5.3: change x−1=t to compute ∫x²/(x−1)³ dx.',
    'Riemann sums — Example 1.1: area under y=x² on [0,1]. Example 1.2: sup/inf of f on [0,1]. Example 1.3: ∫ₐᵇ k dx. Example 1.4: Dirichlet function (0 on Q, 1 on R\\Q) — not integrable.',
    'Example 1.5: ∫₀² E(x) dx (integer part).',
    'Example 2.1 (Barrow): area under y=x² on [0,1]. Example 2.2: average value of E=3 sin 2t on [0, 0.6]. Example 2.3: ∫₁² x eˣ dx (by parts).',
    'Plane areas — Example 3.1: ellipse x²/9 + y²/4 = 1. Example 3.2: area under y=sin x, 0 to 3π. Example 3.3: area between y=2−x² and y=x. Example 3.4: area between OY and x=4−y².',
    'Volumes — Example 4.1: sphere (disc). Example 4.2: torus (washer). Example 4.3: region between x=1 and x=2−y² about x=1. Example 4.4: region between y=1 and y=x² about x=2 (shells).',
    'Arc length — Example 5.1: arc of x²+y²=R² from (0,R) to (R/2, ...).',
]
for i, q in enumerate(examples_int, 1):
    add_para(f'Example {i}. {q}')

add_para('Exercises — Calculation of Primitives（不定积分习题）', size=12, bold=True)
ex_int1 = [
    'Compute ∫(3x² − 2/x + √x) dx.',
    'Compute ∫(1−√x)²/√x dx on ]0,+∞[.',
    'Compute ∫dx/(1+x⁴).',
    'Compute ∫e^{√x}/√x dx on ]0,+∞[.',
    'Compute ∫(x+3)/(x²+2x+5) dx.',
    'Compute ∫cos(5x) cos(3x) dx.',
    'Compute ∫sin(4x) cos x dx.',
    'Compute ∫sin⁴x dx.',
    'Compute ∫x² ln x dx on ]0,+∞[.',
    'Compute ∫arctan x dx.',
    'Compute ∫x² cos x dx.',
    'Compute ∫sin(ln x) dx on ]0,+∞[.',
    'Using the reduction formula of Example 3.5, compute ∫x⁴ eˣ dx.',
    'Obtain a reduction formula for Iₙ=∫(ln x)ⁿ dx (n≥1) on ]0,+∞[; compute ∫(ln x)³ dx.',
    'Compute ∫√(9−x²) dx on ]−3,3[.',
    'Compute ∫dx/(1+√x) on ]0,+∞[.',
    'Compute ∫dx/(1+eˣ).',
    'Compute ∫(x²+2)/(x²−1) dx.',
    'Compute ∫dx/(x+x³).',
    'Compute ∫(x+1)/(x(x−1)²) dx.',
]
for i, q in enumerate(ex_int1, 1):
    add_para(f'Exercise {i}. {q}')

add_para('Exercises — Riemann Integral and Applications（定积分及应用习题）', size=12, bold=True)
ex_int2 = [
    'Compute ∫_{π/2}^π x cos x dx.',
    'Compute ∫₀^{ln3} eˣ/(1+e^{2x}) dx.',
    'Compute ∫₋₂² |x²−1| dx; explain why it differs from ∫₋₂² (x²−1) dx.',
    'Current i(t)=I₀ sin ωt, t∈[0, π/ω]; compute its average value.',
    'Area bounded by y=x, y=x² and the line x=2.',
    '(Listed as Exercise 6 in the original but OCR missed the statement — area between y=x and y=x³ from 0 to 1, or similar; answer not fully legible.)',
    'Volume of a right circular cone (base radius R, height h) as a volume of revolution.',
    'Region bounded by y=x², y=0, x=2; volume about OY — by shells, then by washers.',
    'Volume when region under y=sin x (0≤x≤π) is rotated about OX.',
    'Arc length: (a) y=2x+1, 0≤x≤3; (b) y=2x^{3/2}, 0≤x≤3; (c) y=(eˣ+e^{−x})/2, 0≤x≤ln 2.',
]
for i, q in enumerate(ex_int2, 1):
    add_para(f'Exercise {i}. {q}')

# ---------- Series ----------
add_h2('Unit 5 — Series（级数）')
add_para('Examples', size=12, bold=True)
examples_series = [
    'Example 1.1: convergent series Σ 1/(n(n+1)).',
    'Example 1.2: properly divergent — Σ n. Example 1.3: finitely oscillating — Σ cos(nπ)/n. Example 1.4: infinitely oscillating — Σ n sin((2n−1)π/2).',
    'Geometric series — Example 4.1: (a) Σ_{n≥1} 4(3/π)^{n−1}; (b) Σ_{n≥1} 12/π^{n}; (c) Σ_{n≥1} 2(e/3)^{n−1}.',
    'Telescopic — Example 4.2: (a) Σ 1/(n(n+1)); (b) Σ(√(n+1)−√n); (c) Σ 1/(n(n+2)).',
    'Comparison test — Example 6.1: Σ 1/(3n+1) (divergent); Example 6.2: Σ ln((n−1)/n) (divergent).',
    'Limit comparison — Example 6.3: Σ (3n+2)/(n(n²−1)); Example 6.4: Σ ln n / n²; Example 6.5: Σ (ln n)/n...',
    'D\'Alembert — Example 6.6: Σ 1/n!.',
    'Cauchy (root) — Example 6.7: Σ (1/n)ⁿ.',
    'Raabe — Example 6.8: Wallis series Σ [1·3·5…(2n−1)]/[2·4·6…(2n)]·1/(2n+1).',
    'Integral test — Example 6.9: generalized harmonic series Σ 1/nᵖ.',
    'Leibniz — Example 7.1: alternating harmonic series Σ (−1)^{n+1}/n = ln 2.',
    'Absolute convergence — Example 7.2: Σ sin²(n)/n².',
    'Rearrangement — Example 7.3: rearranging the alternating harmonic series gives (ln 2)/2.',
    'Functional sequences — Example 1.1: fₙ(x)=xⁿ on ]0,1[. Example 1.2: (a) fₙ(x)=n(1−x)ⁿ on [0,1]; (b) fₙ(x)=xⁿ/n on ]0,1[; (c) fₙ(x)=...',
    'M-test — Example 2.1: (a) Σ x²/(1+x²)ⁿ; (b) Σ sin(nx)/n² on R.',
    'Power series — Example 3.1: five series (radius & field of convergence).',
    'Cauchy product — Example 4.1: expansion of h(x)=eˣ/(1+x) about 0.',
]
for i, q in enumerate(examples_series, 1):
    add_para(f'Example {i}. {q}')

add_para('Exercises — Numerical Series（数项级数习题）', size=12, bold=True)
ex_s1 = [
    'Show that Σ_{n≥1} 1/((n+1)(n+2)) converges and compute its sum.',
    'Determine the character of Σ_{n≥1} (−1)ⁿ n/(n+1); classify (properly divergent / finitely / infinitely oscillating).',
    'Study the character of (a) Σ (2n+1)/(n³+5); (b) Σ 1/√(n²+n).',
    'Study the character of Σ n!/nⁿ.',
    'Study the character of Σ (n/(n+1))^{n²}.',
    'Study the character of Σ [1·3·5…(2n−1)]/[2·4·6…(2n)] · 1/(2n+1).',
    'Study the character of (a) Σ 1/(n ln n); (b) Σ 1/(n²(ln n)²), n≥2.',
    'Classify as absolutely / conditionally convergent or divergent: (a) Σ (−1)^{n+1}/n³; (b) Σ cos n / n².',
    'Show D\'Alembert\'s and Cauchy\'s tests are both inconclusive for Σ 1/n and for Σ 1/n²; what does Raabe give?',
]
for i, q in enumerate(ex_s1, 1):
    add_para(f'Exercise {i}. {q}')

add_para('Exercises — Functional Sequences and Series（函数列与函数项级数习题）', size=12, bold=True)
ex_s2 = [
    'Study pointwise and uniform convergence of fₙ(x)=nx/(1+n²x²) on (a) D=[0,1]; (b) D=[1,2].',
    'Let fₙ(x)=xⁿ. Prove uniform convergence on [0,a] for every 0<a<1; prove it is not uniform on [0,1].',
    'Prove uniform convergence (Weierstrass M-test) of (a) Σ xⁿ/n² on [−1,1]; (b) Σ n e^{−nx} on [a,+∞[, a>0. Show (b) is not uniform on ]0,+∞[.',
    'Determine radius R and field of convergence of (a) Σ (x−2)ⁿ/(n 3ⁿ); (b) Σ (x+1)^{2n}/4ⁿ; (c) Σ nⁿ xⁿ/n!.',
    'Starting from the geometric series, prove (a) Σ n xⁿ = x/(1−x)² (|x|<1); (b) Σ xⁿ/n = −ln(1−x), x∈[−1,1[. Deduce Σ n/2ⁿ and Σ (−1)ⁿ/n.',
    'Expand about a=0 (indicate field): (a) 1/(3−x); (b) g(x)=ln(1+2x²); (c) h(x)=∫₀ˣ e^{−t²} dt.',
    'Cauchy product: expand about 0 (a) 1/((1−x)²); (b) h(x)=eˣ sin x up to x⁵.',
    'Failure of transfer theorems: fₙ(x)=n²x(1−x²)ⁿ on [0,1]. Compute pointwise limit f, integrals ∫fₙ; decide uniformity.',
]
for i, q in enumerate(ex_s2, 1):
    add_para(f'Exercise {i}. {q}')

doc.add_page_break()

# ============================================================
# 第三部分：参考答案
# ============================================================
add_h1('第三部分  参考答案')
add_para('说明：以下答案均来自课件原文（Appendix / Answer 部分），未超纲。答案按题目所在主题与编号对应。', size=10)

# ---------- Topic 2 答案 ----------
add_h2('Topic 2 — Exercises 答案')
ans_t2 = [
    '(a) 3/2; (b) 1/2; (c) e⁶.',
    '(a) d=3, a₁=5, a₁₀=32, S₁₀=185; (b) 9.',
    'Decreasing and bounded below by √2, hence convergent, with lim aₙ = √2 (Newton\'s method for x²=2).',
    '(a) 4; (b) 1/2; (c) 3/2.',
    'a = 0 and b = 6.',
    '(a) 1/2; (b) 2/3; (c) e³.',
    'f removable at x=3 (limit 5); g infinite at x=±1; h infinite at x=0, with L⁻=0 and L⁺=+∞.',
    'D_f = R \\ {−1}; vertical x=−1 and oblique y=x−1; no horizontal asymptote.',
    'Bolzano applied to f(x)=eˣ+x−3; two bisections give c∈]3/4, 1[, and f is strictly increasing.',
    '(a) Bolzano applied to g(x)=cos x−x, strictly decreasing; (b) maximum f(2)=2, minimum f(1)=−2.',
    '(a) |aₙ−3|=7/(n+2)<ε if n>7/ε−2, so N=6998; (b) δ=ε/5; (c) N≥√((M+1)/2).',
    '(a) increasing, 1/2≤aₙ<3, →3; (b) decreasing, bounded below, →0; (c) bounded but not monotone: oscillating.',
    '(a) 0; (b) 0; (c) 1.',
    'The three limits are 0; in (b) use 1/(n+1) ≤ Sₙ ≤ n/(n²+1).',
    '(a) xₙ=5(0.8)^{n−1}→0, stable, sum 25, and n=29; (b) 10 steps, and 20 steps.',
    'None exists; (a) L∓=∓1/4; (b) L⁻=1, L⁺=0; (c) two sequences give 1 and −1.',
    '(a) −3/2; (b) y=2 at +∞ and y=−2 at −∞; (c) x=0 only from the right, and y=x+1 on both sides.',
    '(a) −1; (b) 1/2; (c) 1; (d) 1.',
    '(a) opposite signs at ±∞ + Bolzano; (b) ]−2,−1[, ]0,1[, ]1,2[; (c) Darboux with f(0)=−1<5<11=f(2), and f increasing.',
    '(a)–(e) false, with counterexamples (−1)ⁿ, (−1)ⁿ, (x²−1)/(x−1), 1/x on ]0,1] and x²−1 on [−2,2]; (f) true, take ε=L/2.',
]
for i, a in enumerate(ans_t2, 1):
    add_para(f'Exercise {i}. {a}')

# ---------- Topic 3 答案 ----------
add_h2('Topic 3 — Exercises 答案')
ans_t3 = [
    'f\'(1) = −1/4; t: y = −x/4 + 3/4, n: y = 4x − 7/2.',
    'a=2, b=−1; with these values f is differentiable on R.',
    '(a) 1/(1−x²); (b) 2e^{2x}/(1+e^{4x}); (c) x^{sin x}(cos x · ln x + sin x / x).',
    'y\' = (2y − x²)/(y² − 2x); slope −1, tangent y = −x + 6.',
    '(a) c = e−1 ≈ 1.718; (b) apply the theorem to sin and bound |cos c| ≤ 1.',
    'Increasing on ]−∞,−1[ and ]3,+∞[, decreasing on ]−1,3[; max (−1,10), min (3,−22); concave down then up, inflection at (1,−6).',
    'Maximum f(1)=e⁻¹≈0.368; minimum f(0)=0.',
    '60 m parallel to the river, 30 m for each of the other two; 120 m of fence.',
    '(a) 1/2; (b) 1/6; (c) 1.',
    'P₃(x)=1 + x/2 − x²/8 + x³/16; √1.1 ≈ 1.0488125, with |R₃| ≤ 4·10⁻⁶.',
    '(a) Continuous; not differentiable at x=±2 (corners, lateral derivatives −4 and +4); (b) continuous, not differentiable: the quotient tends to +∞ (vertical tangent).',
    '(a) (−3)ⁿ e^{−3x}; (b) (−1)ⁿ n!/(1+x)^{n+1}; (c) sin(x + nπ/2).',
    '(a) ≈2.01 (true 2.00995…); (b) dV/V = 3 dr/r = 3%.',
    '(a) c=2; (b) Bolzano gives one root in ]0,1[, and f\'(x)=3x²+3>0 forbids a second.',
    '(a) g=eˣ−1−x has a global minimum g(0)=0; (b) g=x−sin x has g\'=1−cos x≥0 and g(0)=0.',
    '(1, 1), at distance √5 ≈ 2.236 (minimise the square of the distance).',
    '(a) 0 (form ∞−∞: common denominator first); (b) e^{−1/2}≈0.6065 (form 1^∞: take logarithms first).',
    '(a) 2x − 2x² + (8/3)x³; (b) 1 − x² + x⁴; (c) x² − x⁶/6.',
    '(a) 1/24; (b) f: order 4, even and positive ⇒ local minimum; g: order 3, odd ⇒ inflection, no extremum.',
    '(a) n=7 (bounds for n=5,6,7: 3.6·10⁻⁵, 2.6·10⁻⁶, 1.6·10⁻⁷), giving e^{0.5}≈1.6487212; (b) sin(0.2)≈0.1986667, |R|≤(0.2)⁵/5!≈2.7·10⁻⁶.',
]
for i, a in enumerate(ans_t3, 1):
    add_para(f'Exercise {i}. {a}')

# ---------- Basic Notions 答案 ----------
add_h2('Unit 1 — Exercises 答案')
ans_bn = [
    'True for n=1; the inductive step adds 2n+1 to n² and gives (n+1)².',
    '(a) The argument of Theorem 1.1.7 (√2 irrational), with divisibility by 3 in place of parity. (b) x = 47/110.',
    ']−∞,−3] ∪ [7,+∞[ and ]−1,1/3[; max A = sup A = 5/2, min A = inf A = 1.',
    'z = −1/10 + 7i/10.',
    '−512 − 512√3 i.',
    'z = 1+i, −1+i, −1−i, 1−i; a square of centre the origin and circumradius √2.',
    'cos(3α) = 4 cos³ α − 3 cos α.',
    'ln(−i) = i(−π/2 + 2kπ), k∈Z; Ln(−i) = −iπ/2.',
    'The line y = −x.',
    'Use |z|² = z·z̄; geometrically: the sum of the squares of the diagonals of a parallelogram equals the sum of the squares of its four sides.',
    '±1, ±1/2 ± (√3/2)i — the vertices of a regular hexagon; the sum is a geometric progression of ratio w = e^{2πi/n} ≠ 1 with wⁿ = 1, hence (1−wⁿ)/(1−w) = 0.',
    'D_f = ]−∞,−2[ ∪ ]1,+∞[, R_f = R \\ {0}, and f⁻¹(x) = (1+2eˣ)/(1−eˣ).',
    'f even, unbounded, not periodic; g odd, bounded by 1, not periodic; h neither, bounded by √2, period 2π; and e^{2x} = ch 2x + sh 2x.',
    'f⁻¹(x) = log₂(x/(1−x)) (valid on the appropriate range).',
    'Write u = log_a x so x = aᵘ; take logarithms in base b.',
    'g\'(1) = 1/2.',
    'D_f = R \\ {−1}; (f∘f)(x) = −1/x; (f∘f∘f∘f)(x) = x; f⁻¹(x) = (1+x)/(1−x).',
    '(b) cos(arcsin x) = √(1−x²), tan(arcsin x) = x/√(1−x²) on ]−1,1[; (c) (arcsin x)\' = 1/√(1−x²).',
    'Replace each hyperbolic function by its exponential definition and expand; putting y=x gives the double-argument formulas.',
    '(a) argcoth x = argth(1/x), valid on R\\[−1,1]. (b) x = ±ln 2, with sh x = ±√21/2, th x = ±√21/5; for ch x = a (a≥1): x = ±argch a = ±ln(a+√(a²−1)).',
]
for i, a in enumerate(ans_bn, 1):
    add_para(f'Exercise {i}. {a}')

# ---------- Integral Calculus 答案 ----------
add_h2('Unit 4 — Exercises 答案（不定积分）')
ans_int1 = [
    'x³ − 2 ln|x| + (2/3)x^{3/2} + C.',
    'ln x − 4√x + x + C.',
    '(1/2) arctan(x²) + C.',
    '2 e^{√x} + C.',
    '(1/2) ln|x²+2x+5| + (1/2) arctan((x+1)/2) + C.',
    'sin(8x)/16 + sin(2x)/4 + C.',
    'cos(5x)/10 − cos(3x)/6 + C.',
    '3x/8 − sin(2x)/4 + sin(4x)/32 + C.',
    '(x³/3) ln x − x³/9 + C.',
    'x arctan x − (1/2) ln(1+x²) + C.',
    'x² sin x + 2x cos x − 2 sin x + C.',
    '(x/2)[sin(ln x) − cos(ln x)] + C.',
    'eˣ(x⁴ − 4x³ + 12x² − 24x + 24) + C.',
    'Iₙ = x(ln x)ⁿ − n Iₙ₋₁; ∫(ln x)³ dx = x[(ln x)³ − 3(ln x)² + 6 ln x − 6] + C.',
    '(9/2) arcsin(x/3) + (x/2)√(9−x²) + C.',
    '2√x − 2 ln(1+√x) + C.',
    'x − ln(1+eˣ) + C (or −ln(1+e^{−x}) + C).',
    'x + (3/2) ln|(x−1)/(x+1)| + C.',
    'ln|x| − (1/2) ln(1+x²) + C.',
    'ln|x/(x−1)| − 2/(x−1) + C.',
]
for i, a in enumerate(ans_int1, 1):
    add_para(f'Exercise {i}. {a}')

add_h2('Unit 4 — Exercises 答案（定积分及应用）')
ans_int2 = [
    '−1 − π/2.',
    'arctan 3 − π/4 ≈ 0.4636.',
    '8/3 (vs −4/3 for the integral without absolute value — cancellation against OX).',
    '2 I₀/π ≈ 0.637 I₀.',
    '3/2 − ln 2 ≈ 0.807 square units.',
    '(OCR partially illegible; the exercise concerns an area/volume; please check the original slide.)',
    '(1/3) π R² h.',
    '8π cubic units (both methods).',
    'π²/2 ≈ 4.935 cubic units.',
    '(a) 3√5 ≈ 6.708 linear units; (b) 14/3 ≈ 4.667; (c) 3/4 linear units.',
]
for i, a in enumerate(ans_int2, 1):
    add_para(f'Exercise {i}. {a}')

# ---------- Series 答案 ----------
add_h2('Unit 5 — Exercises 答案（数项级数）')
ans_s1 = [
    'Converges, with sum 1/2 (telescopic: aₙ = 1/(n+1) − 1/(n+2)).',
    'Diverges; more precisely, finitely oscillating — the partial sums have two limit points 1−ln2 and −ln2.',
    '(a) converges (limit comparison with 1/n²); (b) diverges (limit comparison with 1/n).',
    'Converges, since L = 1/e < 1 (D\'Alembert).',
    'Converges, since L = 1/e < 1 (Cauchy / D\'Alembert).',
    'D\'Alembert inconclusive (L=1); Raabe gives R = 3/2 > 1, so the series converges.',
    '(a) diverges (integral test); (b) converges (integral test).',
    '(a) conditionally convergent; (b) absolutely convergent.',
    'Both tests give L=1 for the two series (opposite characters). Raabe gives R=2>1 for Σ1/n², but R=1 for the harmonic series (inconclusive as well).',
]
for i, a in enumerate(ans_s1, 1):
    add_para(f'Exercise {i}. {a}')

add_h2('Unit 5 — Exercises 答案（函数列与函数项级数）')
ans_s2 = [
    '(a) Pointwise limit f=0 on [0,1]; Mₙ = sup = 1/2 → 1/2 ≠ 0, so NOT uniform on [0,1]. (b) Mₙ = n/(1+n²·...) → 0: uniform on [1,2].',
    'On [0,a]: limit f=0 (continuous), sequence decreasing ⇒ Dini gives uniform convergence. On [0,1]: limit f(x)=0 for x∈[0,1[, f(1)=1/2, discontinuous ⇒ not uniform.',
    '(a) Mₙ = 1/n², convergent p-series (p=2>1). (b) Mₙ = n e^{−na} = n qⁿ with q=e^{−a}∈]0,1[, convergent. On ]0,+∞[ the sum S(x)=eˣ/(eˣ−1) is unbounded as x→0+ while every partial sum is bounded, so not uniform there.',
    '(a) R=3, field [−1, 5[ (converges at −1 by Leibniz, diverges at 5: harmonic). (b) p=2, R=2, field ]−3, 1[ (both endpoints diverge). (c) R=e, field ]−e, e[ (both endpoints diverge).',
    '(a) Differentiate the geometric series and multiply by x; Σ n 2^{−n} = 2. (b) Integrate term by term; the field gains x=−1, where Σ(−1)ⁿ/n = −ln 2.',
    '(a) Σ_{n≥0} xⁿ/3^{n+1} on ]−3,3[; (b) Σ_{n≥1} (−1)^{n−1} 2ⁿ x^{2n}/n on [−1/√2, 1/√2]; (c) Σ_{n≥0} (−1)ⁿ x^{2n+1}/(n!(2n+1)) on R.',
    '(a) cₙ = n+1, so 1/(1−x)² = Σ_{n≥0} (n+1)xⁿ; (b) eˣ sin x = x + x² + x³/3 − x⁵/30 + ..., R=+∞.',
    'f=0, but ∫₀¹ fₙ = n²/(2(n+1)) → +∞ ≠ ∫₀¹ f. By Theorem 3(ii) the convergence cannot be uniform; indeed Mₙ → +∞.',
]
for i, a in enumerate(ans_s2, 1):
    add_para(f'Exercise {i}. {a}')

doc.add_page_break()

# ============================================================
# 第四部分：Example（例题）答案
# ============================================================
add_h1('第四部分  Example（例题）答案')
add_para('说明：本部分给出第二部分所列全部 Example 的解答结果（结论），编号与第二部分的 Example 一一对应。这些例题在原课件中多带完整推导，此处给出最终结果；中英对照，便于核对。', size=10)

# ---------- Topic 2 例题答案 ----------
add_h2('Topic 2 — Example 答案')
ex_ans_t2 = [
    'Strictly increasing and bounded: 0 < aₙ < 1 for all n; sup aₙ = 1 (never attained).　| 严格递增且有界：对一切 n 有 0 < aₙ < 1；上确界为 1（取不到）。',
    'Take N = ⌈5/ε − 3⌉; for ε = 0.01, N = 497.　| 取 N = ⌈5/ε − 3⌉；当 ε=0.01 时 N=497。',
    'Increasing and bounded above by 3, hence convergent; the limit is e ≈ 2.71828.　| 递增且有上界 3，故收敛；极限为 e ≈ 2.71828。',
    'a₂₀ = 5 + 19·3 = 62; S₂₀ = (5+62)·20/2 = 670.　| a₂₀ = 62；S₂₀ = 670。',
    '(a) Geometric with r = 1/3: sum S = 2/(1−1/3) = 3. (b) 0.9̄ = 1 (same real number).　| (a) 公比 r=1/3 的几何级数，和 S=3。(b) 0.9̄ = 1（与 1 是同一个实数）。',
    '(a) lim = 5, take δ = ε/2. (b) lim = 2.　| (a) 极限为 5，取 δ=ε/2。(b) 极限为 2。',
    'Does not exist: along xₙ=1/(nπ) the values → 0, along xₙ=1/(2nπ+π/2) the values → 1.　| 不存在：沿数列 xₙ=1/(nπ) 趋于 0，沿 xₙ=1/(2nπ+π/2) 趋于 1。',
    '(a) L⁺=1, L⁻=−1, so the limit at 0 does not exist. (b) k = 7 (so that L⁺=L⁻=5).　| (a) 右极限 1、左极限 −1，故 0 点极限不存在。(b) k=7（使左右极限均为 5）。',
    'By the squeeze rule, −|x| ≤ x·sin(1/x) ≤ |x| → 0, so the limit is 0.　| 由夹逼准则，−|x| ≤ x·sin(1/x) ≤ |x| → 0，故极限为 0。',
    'Vertical asymptote x = 1; oblique asymptote y = 2x + 2; no horizontal asymptote.　| 垂直渐近线 x=1；斜渐近线 y=2x+2；无水平渐近线。',
    '(a) 3/5; (b) 1/2; (c) e⁶.　| (a) 3/5；(b) 1/2；(c) e⁶。',
    'Direct substitution: (1·1 + 2)/√(0+9) = 3/3 = 1.　| 直接代入：(1+2)/3 = 1。',
    'Removable (redefine f(2)=4); infinite (g=1/(x−3), vertical asymptote x=3); jump (h with jump −3 at 0); essential (sin(1/x)-type).　| 可去（令 f(2)=4）；无穷（g=1/(x−3)，垂直渐近线 x=3）；跳跃（h 在 0 处跃度 −3）；本性（sin(1/x) 型）。',
    'f(0)=−1<0, f(1)=1>0, so a root lies in ]0,1[; after two bisections, c ∈ ]1/2, 3/4[; f′(x)=3x²+1>0, so the root is unique.　| f(0)<0<f(1)，故 ]0,1[ 内有根；两次二分后 c∈]1/2,3/4[；f′>0，故根唯一。',
    'Apply the Intermediate Value Theorem to g(x)=f(x)−x on [0,1]: g(0)≥0, g(1)≤0, so g(c)=0, i.e. f(c)=c.　| 对 g(x)=f(x)−x 在 [0,1] 上用介值定理：g(0)≥0、g(1)≤0，故存在 c 使 g(c)=0，即 f(c)=c。',
]
for i, a in enumerate(ex_ans_t2, 1):
    add_para(f'Example {i}. {a}')

# ---------- Topic 3 例题答案 ----------
add_h2('Topic 3 — Example 答案')
ex_ans_t3 = [
    'f′(4) = 1/4; tangent t: y = x/4 + 1; normal n: y = −4x + 18.　| f′(4)=1/4；切线 y=x/4+1；法线 y=−4x+18。',
    'f′(0⁺) = 1, f′(0⁻) = −1; the two are different, so f is not differentiable at 0 (corner).　| 右导数 1、左导数 −1，不相等，故 0 处不可导（角点）。',
    '(a) y′ = x/(1+x²); (b) y′ = 2e^{2x}/(1+e^{4x}); (c) quotient rule: [(2x sinx + x² cosx)(1+x) − x² sinx]/(1+x)².　| (a) x/(1+x²)；(b) 2e^{2x}/(1+e^{4x})；(c) 商的导数如上。',
    '(xˣ)′ = xˣ(ln x + 1); implicitly y′ = −x/y, so at (3,4): y′ = −3/4.　| (xˣ)′=xˣ(lnx+1)；隐式求导 y′=−x/y，在 (3,4) 处为 −3/4。',
    '(a) √4.05 ≈ 2 + 0.05/4 = 2.0125. (b) dA = 0.4 cm², relative error 0.4%.　| (a) ≈2.0125；(b) 面积微分 dA=0.4 cm²，相对误差 0.4%。',
    'Increasing on ]−∞,−1[ and ]3,+∞[, decreasing on ]−1,3[; local max (−1,10), local min (3,−22); inflection point (1,−6).　| 在 ]−∞,−1[ 与 ]3,+∞[ 递增，]−1,3[ 递减；极大 (−1,10)，极小 (3,−22)；拐点 (1,−6)。',
    '(a) 1/2; (b) 0; (c) 0, hence lim_{x→0⁺} xˣ = 1.　| (a) 1/2；(b) 0；(c) 0，从而 lim xˣ = 1。',
    'Corner squares of side x = 2 cm give maximum volume V = 128 cm³.　| 剪去角块边长 x=2 cm 时体积最大，V=128 cm³。',
    'h = 2r (height equals the diameter) minimizes the surface area.　| 当 h=2r（高等于直径）时表面积最小。',
    'P₁(x) = x; P₃(x) = x − x³/3!; P₅(x) = x − x³/3! + x⁵/5! (only odd powers).　| P₁=x；P₃=x−x³/6；P₅=x−x³/6+x⁵/120（仅奇次项）。',
    'P₃ gives e^{0.1} ≈ 1.105167 with |R₃| ≤ 5×10⁻⁶; for error < 10⁻⁸ one needs n = 5.　| P₃ 给出 e^{0.1}≈1.105167，误差 ≤5×10⁻⁶；误差 <10⁻⁸ 需取 n=5。',
    'ln(1+x): Pₙ = x − x²/2 + x³/3 − … + (−1)^{n−1}xⁿ/n, radius 1, and at x=1 the sum is ln 2. 1/(1−x): Pₙ = 1+x+…+xⁿ, remainder x^{n+1}/(1−x) → 0 only if |x|<1. cosh x: P₀=P₁=1, P₂=P₃=1+x²/2!, P₄=P₅=1+x²/2!+x⁴/4!, converges for all x.　| 三者的泰勒多项式及收敛范围如上。',
    'P₄(x) = 1 − x² + x⁴/2; small-angle: sin x ≈ x with error ≤ |x|³/6.　| P₄=1−x²+x⁴/2；小角度近似 sin x≈x，误差 ≤|x|³/6。',
    'lim = 1/6; criterion: if the first non-vanishing derivative at x₀ has even order n with f⁽ⁿ⁾(x₀)>0 it is a minimum (<0 a maximum); if odd order it is an inflection point (no extremum).　| 极限为 1/6；判据：首个非零导数阶数为偶且系数正/负 ⇒ 极小/极大；阶数为奇 ⇒ 拐点（无极值）。',
]
for i, a in enumerate(ex_ans_t3, 1):
    add_para(f'Example {i}. {a}')

# ---------- Unit 1 例题答案 ----------
add_h2('Unit 1 — Example 答案')
ex_ans_bn = [
    'min A = inf A = 0; sup A = 1, max A does not exist (1 ∉ A).　| min A = inf A = 0；sup A = 1，最大值不存在。',
    'z₁+z₂ = (7,8); z₁−z₂ = (−1,2); z₁z₂ = (−3,29).　| 和 (7,8)；差 (−1,2)；积 (−3,29)。',
    'Binomial form: 7+8i and −3+29i. Roots of x²+x+1=0: x = −1/2 ± (√3/2)i.　| 二项形式 7+8i、−3+29i；方程根为 −1/2 ± (√3/2)i。',
    'Modulus |z₁|=√34, |z₂|=5; distance |z₁−z₂|=√5.　| |z₁|=√34，|z₂|=5；距离 |z₁−z₂|=√5。',
    '(3+5i)/(−2−3i) = −21/13 − (1/13)i.　| 商为 −21/13 − (1/13)i。',
    '|−1+i| = √2; principal argument Arg(−1+i) = 3π/4.　| 模 √2；主辐角 3π/4。',
    'arg_{6π}(−1+i) = 3π/4 + 2π = 11π/4; arg_{7π}(−1+i) = 3π/4; arg_{7π/4}(−1+i) = 3π/4 − 2π = −5π/4.　| 各辐角分支分别为 11π/4、3π/4、−5π/4。',
    '2−2i → (2√2, −π/4); i → (1, π/2); −1+√3 i → (2, 2π/3).　| 极坐标/三角形式如上。',
    'sin(3α) = 3 cos²α sinα − sin³α (equivalently 3 sinα − 4 sin³α).　| sin(3α) = 3sinα − 4sin³α。',
    '√i = ±(cos π/4 + i sin π/4) = ±(√2/2 + √2/2 i); roots of z⁴−16=0: 2, 2i, −2, −2i.　| √i = ±(√2/2 + √2/2 i)；z⁴−16=0 的根为 ±2、±2i。',
    'e^{iπ/2}=i; e^{±iπ}=−1; e^{i3π/2}=−i; e^{−iπ/2}=−i; e^{2iπ}=1.　| 各值分别为 i、−1、−i、−i、1。',
    '−1+i = √2 e^{i3π/4}; Ln(−1+i) = (ln2)/2 + i 3π/4; 1/(1+i)⁸ = 1/16; (1−i)^{2i}/(1+√3 i) in exponential form = 2^{i−1/2} e^{π/2 − i π/3}.　| 指数形式与对数值如上；1/(1+i)⁸=1/16。',
    'f∘g = g∘f = x, so they are inverses; f⁻¹(x) = ∛((x−2)/5).　| 验证互为反函数；反函数 f⁻¹(x)=∛((x−2)/5)。',
    'g′(x) = 1/f′(g(x)) = 1/[15·((x−2)/5)^{2/3}].　| 反函数导数 g′(x) 如上。',
    '∫(2x+3)/(x²+3x+7) dx = ln|x²+3x+7| + C; ∫x e^{x²} dx = (1/2)e^{x²} + C; ∫3x²(x²+1) dx = 3x⁵/5 + x³ + C.　| 三个直接积分结果分别为 ln|x²+3x+7|+C、(1/2)e^{x²}+C、3x⁵/5+x³+C。',
]
for i, a in enumerate(ex_ans_bn, 1):
    add_para(f'Example {i}. {a}')

# ---------- Unit 4 例题答案 ----------
add_h2('Unit 4 — Example 答案')
ex_ans_int = [
    'F′(x) = sin x + x cos x − sin x = x cos x = f(x), so F is a primitive.　| F′=x cos x=f(x)，故 F 是原函数。',
    '∫(2x+3)/(x²+3x+7) dx = ln|x²+3x+7| + C; ∫x e^{x²} dx = (1/2)e^{x²} + C; ∫3x²(x²+1) dx = 3x⁵/5 + x³ + C.　| 三个复合积分结果如上。',
    '1.3: x⁵/5 − x³ + 5x + C. 1.4: tan x − x + C. 1.5: ln|tan x| + C.　| 分别为 x⁵/5−x³+5x+C；tan x−x+C；ln|tan x|+C。',
    '∫√((1−x)/(1+x)) dx = arcsin x + √(1−x²) + C on ]−1,1[.　| 结果为 arcsin x + √(1−x²) + C。',
    '∫sin(3x+5)cos(2x−3) dx = −cos(5x+2)/10 − cos(x+8)/2 + C.　| 积化和差后结果如上。',
    '∫x² eˣ dx = (x² − 2x + 2)eˣ + C.　| 分部积分得 (x²−2x+2)eˣ + C。',
    '3.1: (1+x)ln(1+x) − x + C. 3.2: x arcsin x + √(1−x²) + C.　| 分别为 (1+x)ln(1+x)−x+C；x arcsin x+√(1−x²)+C。',
    '∫e^{ax}cos(bx) dx = e^{ax}(a cos bx + b sin bx)/(a²+b²) + C; ∫e^{ax}sin(bx) dx = e^{ax}(a sin bx − b cos bx)/(a²+b²) + C.　| 两个自回归积分结果如上。',
    '∫sin²x dx = x/2 − sin 2x/4 + C; ∫cos²x dx = x/2 + sin 2x/4 + C.　| 分别为 x/2 − sin2x/4 + C；x/2 + sin2x/4 + C。',
    'Reduction: Iₙ = xⁿ eˣ − n Iₙ₋₁; I₃ = (x³ − 3x² + 6x − 6)eˣ + C.　| 递推 Iₙ=xⁿeˣ−nIₙ₋₁；I₃=(x³−3x²+6x−6)eˣ+C。',
    '4.1: 2 arcsin(x/2) + (x/2)√(4−x²) + C. 4.2: cos x·(1 − ln(cos x)) + C.　| 换元结果分别如上。',
    'Polynomial division: 2x³/3 + x²/2 − (7/2)ln|2x+1| + C.　| 多项式除法后结果如上。',
    '(a) (13/10)ln|x−1| − (1/2)ln|x+1| + (1/5)ln|x+4| + C. (c) ln|x−1| − 1/(x−1) − 1/[2(x−1)²] + C. (d) (2/3)arctan x − (1/3)arctan(x/2) + C. (e) 2ln|x−4| − (3/2)ln(x²+x+1) − (5/√3)arctan((2x+1)/√3) + C.　| 各部分分式积分结果如上。',
    'Change x−1=t gives ln|x−1| − 2/(x−1) − 1/[2(x−1)²] + C.　| 换元后结果如上。',
    '1.1: area = 1/3. 1.2: sup=1, inf=0. 1.3: ∫ₐᵇ k dx = k(b−a). 1.4: the Dirichlet-type function is bounded but NOT integrable.　| 面积 1/3；上确界 1、下确界 0；∫ₐᵇk dx=k(b−a)；狄利克雷型函数有界但不可积。',
    '∫₀² E(x) dx = 1 (integer-part function).　| 取整函数积分结果为 1。',
    '2.1: ∫₀¹ x² dx = 1/3. 2.2: average = (5/2)(1 − cos 1.2) ≈ 1.594. 2.3: ∫₁² x eˣ dx = 1 + e².　| 分别为 1/3；≈1.594；1+e²。',
    '3.1: ellipse area = 6π. 3.2: area under sin x on [0,3π] = 6. 3.3: area between 2−x² and x = 9/2. 3.4: area between OY and x=4−y² = 32/3.　| 各平面面积如上。',
    '4.1: sphere V = (4/3)πR³. 4.2: torus V = 2π²Rr². 4.3: V = 16π/15. 4.4: shells give V = 5π/6.　| 各旋转体体积如上。',
    'Arc of the circle from (0,R) to (R/2, (R√3)/2): L = πR/6.　| 圆弧长 L = πR/6。',
]
for i, a in enumerate(ex_ans_int, 1):
    add_para(f'Example {i}. {a}')

# ---------- Unit 5 例题答案 ----------
add_h2('Unit 5 — Example 答案')
ex_ans_series = [
    'Convergent telescopic series with sum 1.　| 收敛的望远镜级数，和为 1。',
    '1.2: properly divergent to +∞. 1.3: finitely oscillating. 1.4: infinitely oscillating.　| 分别为正常发散到 +∞；有限振荡；无限振荡。',
    '(a) r = π/3 > 1 ⇒ divergent (to +∞). (b) r = 1/π < 1 ⇒ sum = 12/(π−1) ≈ 5.50. (c) r = e/3 < 1 ⇒ sum = 2/(1−e/3) ≈ 8.65 (geometric).　| (a) 发散；(b)(c) 收敛，和分别约为 5.50、8.65。',
    '(a) sum = 1. (b) Sₙ = √(n+1) − 1 → +∞, divergent. (c) sum = 3/4.　| (a) 和为 1；(b) 发散；(c) 和为 3/4。',
    '6.1: 1/(3n+1) behaves like 1/n ⇒ divergent. 6.2: ln((n−1)/n) ~ −1/n ⇒ divergent.　| 两级数均发散。',
    '6.3 (l=3): converges. 6.4 (l=0): Σ ln n / n² converges. 6.5 (l=∞): Σ (ln n)/n diverges.　| 6.3、6.4 收敛，6.5 发散。',
    'L = 0 < 1 ⇒ convergent.　| L=0<1，收敛。',
    'L = 1/e < 1 ⇒ convergent.　| L=1/e<1，收敛。',
    "D'Alembert inconclusive (L=1); Raabe gives R = 1/2 < 1 ⇒ divergent.　| 比值法失效，拉阿伯判别 R=1/2<1，发散。",
    'Converges iff p > 1 (generalized harmonic series / p-series).　| 当且仅当 p>1 时收敛。',
    'Converges (conditionally) with sum ln 2.　| 条件收敛，和为 ln 2。',
    '|sin²(n)/n²| ≤ 1/n², so it is absolutely convergent (hence convergent).　| 绝对收敛（从而收敛）。',
    'Rearranged \"one positive, two negative\": the new sum is (ln 2)/2 ≠ ln 2 (Riemann rearrangement).　| 重排后和为 (ln 2)/2（与原和不同）。',
    '1.1: fₙ(x)=xⁿ → 0 pointwise on ]0,1[. 1.2(a): Mₙ = n/((n+1)(1−1/(n+1))ⁿ) → e⁻¹ ≠ 0, NOT uniform on [0,1]. 1.2(b): Mₙ = 1/(n e) → 0, uniform on ]0,1[.　| 1.1 逐点收敛于 0；1.2(a) 不一致收敛；1.2(b) 一致收敛。',
    '(a) converges uniformly on any interval not containing 0 (e.g. [a,b] with a>0) by the M-test; (b) |sin(nx)/n²| ≤ 1/n², uniformly convergent on R.　| (a) 在不含 0 的区间上一致收敛；(b) 在 R 上一致收敛。',
    '(a) R = e, field ]1−e, 1+e[. (b) R = 9, field ]−12, 6[. (c) R = 0, field {1}. (d) R = +∞, field R. (e) R = 2, field ]−2, 2].　| 五个级数的收敛半径与收敛域如上。',
    'Cauchy product: eˣ/(1+x) = 1 + x²/2 − x³/3 + 3x⁴/8 − 11x⁵/30 + … on ]−1,1[ (c₀=1, c₁=0, c₂=1/2, c₃=−1/3).　| 柯西乘积展开如上。',
]
for i, a in enumerate(ex_ans_series, 1):
    add_para(f'Example {i}. {a}')

doc.add_page_break()

# ============================================================
# 第五部分：中文版答案（与题目一一对应）
# ============================================================
add_h1('第五部分  中文版答案')
add_para('说明：本部分为第三部分参考答案（Exercise 答案）的中文表述，编号与第二部分的习题（Exercise）一一对应，方便对照阅读。', size=10)

# ---------- Topic 2 中文答案 ----------
add_h2('Topic 2 — 习题答案（数列与极限）')
zh_t2 = [
    '(a) 3/2；(b) 1/2；(c) e⁶。',
    '(a) 公差 d=3，首项 a₁=5，a₁₀=32，前 10 项和 S₁₀=185；(b) 级数和为 9。',
    '数列递减且有下界 √2，故收敛，极限 lim aₙ = √2（即求 x²=2 的牛顿迭代法）。',
    '(a) 4；(b) 1/2；(c) 3/2。',
    'a = 0，b = 6。',
    '(a) 1/2；(b) 2/3；(c) e³。',
    'f 在 x=3 处为可去间断点（极限为 5）；g 在 x=±1 处为无穷间断点；h 在 x=0 处为无穷间断点，左极限 L⁻=0，右极限 L⁺=+∞。',
    '定义域 D_f = R \\ {−1}；垂直渐近线 x=−1，斜渐近线 y=x−1；无水平渐近线。',
    '对 f(x)=eˣ+x−3 应用波尔查诺定理；两次二分得 c∈]3/4, 1[，且 f 严格递增，故解唯一。',
    '(a) 对 g(x)=cos x−x 应用波尔查诺定理，g 严格递减，故解唯一；(b) 最大值 f(2)=2，最小值 f(1)=−2。',
    '(a) |aₙ−3|=7/(n+2)<ε 等价于 n>7/ε−2，故 N=6998；(b) δ=ε/5；(c) N≥√((M+1)/2)。',
    '(a) 递增，1/2≤aₙ<3，极限为 3；(b) 递减、有下界，极限为 0；(c) 有界但不单调：振荡。',
    '(a) 0；(b) 0；(c) 1。',
    '三个极限均为 0；第 (b) 题用不等式 1/(n+1) ≤ Sₙ ≤ n/(n²+1) 夹逼。',
    '(a) xₙ=5(0.8)^{n−1}→0，模型稳定，振幅总和为 25，首次 xₙ<10⁻² 对应 n=29；(b) 误差低于 10⁻³ 需 10 步，低于 10⁻⁶ 需 20 步。',
    '三个极限都不存在；(a) 左、右极限分别为 ∓1/4；(b) 左极限 L⁻=1，右极限 L⁺=0；(c) 取两个数列分别得到 1 和 −1。',
    '(a) −3/2；(b) 在 +∞ 处水平渐近线 y=2，在 −∞ 处 y=−2；(c) 仅在右侧有垂直渐近线 x=0，两侧斜渐近线均为 y=x+1。',
    '(a) −1；(b) 1/2；(c) 1；(d) 1。',
    '(a) 奇次多项式在 ±∞ 处异号 + 波尔查诺定理；(b) 三个解分别位于 ]−2,−1[、]0,1[、]1,2[；(c) 由达布定理，f(0)=−1<5<11=f(2)，且 f 递增，故取值 5 且仅一次。',
    '(a)–(e) 均为假，反例分别为 (−1)ⁿ、 (−1)ⁿ、 (x²−1)/(x−1)、 ]0,1] 上的 1/x、 [−2,2] 上的 x²−1；(f) 为真，取 ε=L/2 即可。',
]
for i, a in enumerate(zh_t2, 1):
    add_para(f'习题 {i}. {a}')

# ---------- Topic 3 中文答案 ----------
add_h2('Topic 3 — 习题答案（微分学）')
zh_t3 = [
    'f\'(1) = −1/4；切线 t：y = −x/4 + 3/4，法线 n：y = 4x − 7/2。',
    'a=2，b=−1；此时 f 在整个 R 上可导。',
    '(a) 1/(1−x²)；(b) 2e^{2x}/(1+e^{4x})；(c) x^{sin x}(cos x·ln x + sin x / x)。',
    'y\' = (2y − x²)/(y² − 2x)；在 (3,3) 处斜率为 −1，切线为 y = −x + 6。',
    '(a) c = e−1 ≈ 1.718；(b) 对 sin x 应用拉格朗日中值定理，并利用 |cos c| ≤ 1。',
    '在 ]−∞,−1[ 和 ]3,+∞[ 上递增，在 ]−1,3[ 上递减；极大值点 (−1,10)，极小值点 (3,−22)；先下凹后上凹，拐点为 (1,−6)。',
    '最大值 f(1)=e⁻¹≈0.368；最小值 f(0)=0。',
    '平行于河的边长 60 m，另外两边各 30 m；共需围栏 120 m。',
    '(a) 1/2；(b) 1/6；(c) 1。',
    'P₃(x)=1 + x/2 − x²/8 + x³/16；√1.1 ≈ 1.0488125，误差 |R₃| ≤ 4·10⁻⁶。',
    '(a) 连续；在 x=±2 处不可导（角点，左、右导数分别为 −4 和 +4）；(b) 连续但不可导：差商趋于 +∞，有垂直切线。',
    '(a) (−3)ⁿ e^{−3x}；(b) (−1)ⁿ n!/(1+x)^{n+1}；(c) sin(x + nπ/2)。',
    '(a) ≈2.01（真值 2.00995…）；(b) 体积的相对误差 dV/V = 3 dr/r = 3%。',
    '(a) c=2；(b) 由波尔查诺定理在 ]0,1[ 内有一个根，而 f\'(x)=3x²+3>0 排除了第二个根。',
    '(a) 辅助函数 g=eˣ−1−x 在 x=0 处取全局最小值 0；(b) 辅助函数 g=x−sin x 满足 g\'=1−cos x≥0 且 g(0)=0。',
    '最近点为 (1, 1)，距离为 √5 ≈ 2.236（最小化距离的平方）。',
    '(a) 0（∞−∞ 型，先通分）；(b) e^{−1/2}≈0.6065（1^∞ 型，先取对数）。',
    '(a) 2x − 2x² + (8/3)x³；(b) 1 − x² + x⁴；(c) x² − x⁶/6。',
    '(a) 1/24；(b) f：4 阶、偶阶且系数为正 ⇒ 局部最小值；g：3 阶、奇阶 ⇒ 拐点，无极值。',
    '(a) n=7（n=5,6,7 的误差界分别为 3.6·10⁻⁵、2.6·10⁻⁶、1.6·10⁻⁷），得 e^{0.5}≈1.6487212；(b) sin(0.2)≈0.1986667，误差 |R|≤(0.2)⁵/5!≈2.7·10⁻⁶。',
]
for i, a in enumerate(zh_t3, 1):
    add_para(f'习题 {i}. {a}')

# ---------- Unit 1 中文答案 ----------
add_h2('Unit 1 — 习题答案（基本概念）')
zh_bn = [
    'n=1 时成立；归纳步在 n² 基础上加 2n+1 即得 (n+1)²。',
    '(a) 参照定理 1.1.7（√2 无理）的证明，把奇偶性替换为被 3 整除性即可。(b) x = 47/110。',
    '解集为 ]−∞,−3] ∪ [7,+∞[ 和 ]−1,1/3[；max A = sup A = 5/2，min A = inf A = 1。',
    'z = −1/10 + 7i/10。',
    '−512 − 512√3 i。',
    'z = 1+i, −1+i, −1−i, 1−i；四个点构成以原点为中心、外接圆半径为 √2 的正方形。',
    'cos(3α) = 4 cos³ α − 3 cos α。',
    'ln(−i) = i(−π/2 + 2kπ)，k∈Z；主值 Ln(−i) = −iπ/2。',
    '为直线 y = −x。',
    '利用 |z|² = z·z̄；几何意义：平行四边形两条对角线的平方和等于四条边的平方和。',
    '六个六次单位根为 ±1, ±1/2 ± (√3/2)i，对应正六边形的顶点；其和是公比 w = e^{2πi/n} ≠ 1、且 wⁿ = 1 的等比级数，故和为 (1−wⁿ)/(1−w) = 0。',
    '定义域 D_f = ]−∞,−2[ ∪ ]1,+∞[，值域 R_f = R \\ {0}，反函数 f⁻¹(x) = (1+2eˣ)/(1−eˣ)。',
    'f 为偶函数、无界、非周期；g 为奇函数、以 1 为界、非周期；h 既非奇也非偶、以 √2 为界、周期为 2π；且 e^{2x} = ch 2x + sh 2x。',
    '反函数 f⁻¹(x) = log₂(x/(1−x))（在相应值域上成立）。',
    '令 u = log_a x，则 x = aᵘ，两边取以 b 为底的对数即可。',
    'g\'(1) = 1/2。',
    '定义域 D_f = R \\ {−1}；(f∘f)(x) = −1/x；(f∘f∘f∘f)(x) = x；反函数 f⁻¹(x) = (1+x)/(1−x)。',
    '(b) cos(arcsin x) = √(1−x²)，tan(arcsin x) = x/√(1−x²)，在 ]−1,1[ 上成立；(c) (arcsin x)\' = 1/√(1−x²)。',
    '将每个双曲函数代回指数定义并展开；令 y=x 即得二倍角公式。',
    '(a) argcoth x = argth(1/x)，在 R\\[−1,1] 上成立。(b) x = ±ln 2，对应 sh x = ±√21/2，th x = ±√21/5；对 ch x = a（a≥1），解为 x = ±argch a = ±ln(a+√(a²−1))。',
]
for i, a in enumerate(zh_bn, 1):
    add_para(f'习题 {i}. {a}')

# ---------- Unit 4 中文答案 ----------
add_h2('Unit 4 — 习题答案（不定积分）')
zh_int1 = [
    'x³ − 2 ln|x| + (2/3)x^{3/2} + C。',
    'ln x − 4√x + x + C。',
    '(1/2) arctan(x²) + C。',
    '2 e^{√x} + C。',
    '(1/2) ln|x²+2x+5| + (1/2) arctan((x+1)/2) + C。',
    'sin(8x)/16 + sin(2x)/4 + C。',
    'cos(5x)/10 − cos(3x)/6 + C。',
    '3x/8 − sin(2x)/4 + sin(4x)/32 + C。',
    '(x³/3) ln x − x³/9 + C。',
    'x arctan x − (1/2) ln(1+x²) + C。',
    'x² sin x + 2x cos x − 2 sin x + C。',
    '(x/2)[sin(ln x) − cos(ln x)] + C。',
    'eˣ(x⁴ − 4x³ + 12x² − 24x + 24) + C。',
    '递推公式 Iₙ = x(ln x)ⁿ − n Iₙ₋₁；∫(ln x)³ dx = x[(ln x)³ − 3(ln x)² + 6 ln x − 6] + C。',
    '(9/2) arcsin(x/3) + (x/2)√(9−x²) + C。',
    '2√x − 2 ln(1+√x) + C。',
    'x − ln(1+eˣ) + C（或写作 −ln(1+e^{−x}) + C）。',
    'x + (3/2) ln|(x−1)/(x+1)| + C。',
    'ln|x| − (1/2) ln(1+x²) + C。',
    'ln|x/(x−1)| − 2/(x−1) + C。',
]
for i, a in enumerate(zh_int1, 1):
    add_para(f'习题 {i}. {a}')

add_h2('Unit 4 — 习题答案（定积分及应用）')
zh_int2 = [
    '−1 − π/2。',
    'arctan 3 − π/4 ≈ 0.4636。',
    '8/3（相比之下，不带绝对值的积分结果为 −4/3，差在与 OX 轴下方部分的抵消）。',
    '2 I₀/π ≈ 0.637 I₀。',
    '3/2 − ln 2 ≈ 0.807 平方单位。',
    '（原课件该页 OCR 识别不完整，请核对原 PDF 第 66 页。）',
    '(1/3) π R² h。',
    '8π 立方单位（两种方法结果一致）。',
    'π²/2 ≈ 4.935 立方单位。',
    '(a) 3√5 ≈ 6.708 长度单位；(b) 14/3 ≈ 4.667；(c) 3/4 长度单位。',
]
for i, a in enumerate(zh_int2, 1):
    add_para(f'习题 {i}. {a}')

# ---------- Unit 5 中文答案 ----------
add_h2('Unit 5 — 习题答案（数项级数）')
zh_s1 = [
    '收敛，和为 1/2（裂项相消：aₙ = 1/(n+1) − 1/(n+2)）。',
    '发散；更准确地说是有限振荡——部分和有两个极限点 1−ln2 和 −ln2。',
    '(a) 收敛（与 1/n² 极限比较）；(b) 发散（与 1/n 极限比较）。',
    '收敛，因为 L = 1/e < 1（达朗贝尔判别法）。',
    '收敛，因为 L = 1/e < 1（柯西 / 达朗贝尔判别法）。',
    '达朗贝尔判别法失效（L=1）；拉阿伯判别法给出 R = 3/2 > 1，故级数收敛。',
    '(a) 发散（积分判别法）；(b) 收敛（积分判别法）。',
    '(a) 条件收敛；(b) 绝对收敛。',
    '两个级数两种判别法均给出 L=1（敛散性相反）。拉阿伯判别法对 Σ1/n² 给出 R=2>1，但对调和级数给出 R=1，同样失效。',
]
for i, a in enumerate(zh_s1, 1):
    add_para(f'习题 {i}. {a}')

add_h2('Unit 5 — 习题答案（函数列与函数项级数）')
zh_s2 = [
    '(a) 在 [0,1] 上逐点极限 f=0；Mₙ = 上确界 = 1/2 → 1/2 ≠ 0，故在 [0,1] 上不一致收敛。(b) Mₙ → 0：在 [1,2] 上一致收敛。',
    '在 [0,a] 上：极限 f=0（连续），数列递减 ⇒ 由迪尼定理得一致收敛。在 [0,1] 上：极限 f(x)=0（x∈[0,1[），f(1)=1/2，不连续 ⇒ 不一致收敛。',
    '(a) Mₙ = 1/n²，是收敛的 p 级数（p=2>1）。(b) Mₙ = n e^{−na} = n qⁿ，其中 q=e^{−a}∈]0,1[，收敛。在 ]0,+∞[ 上和函数 S(x)=eˣ/(eˣ−1) 在 x→0+ 时无界，而每个部分和都有界，故在该区间上不一致收敛。',
    '(a) R=3，收敛域 [−1, 5[（在 −1 处由莱布尼茨判别法收敛，在 5 处为调和级数发散）。(b) p=2，R=2，收敛域 ]−3, 1[（两端点均发散）。(c) R=e，收敛域 ]−e, e[（两端点均发散）。',
    '(a) 对几何级数逐项求导再乘以 x；Σ n 2^{−n} = 2。(b) 逐项积分；收敛域在 x=−1 处扩大，此时 Σ(−1)ⁿ/n = −ln 2。',
    '(a) Σ_{n≥0} xⁿ/3^{n+1}，在 ]−3,3[ 上成立；(b) Σ_{n≥1} (−1)^{n−1} 2ⁿ x^{2n}/n，在 [−1/√2, 1/√2] 上成立；(c) Σ_{n≥0} (−1)ⁿ x^{2n+1}/(n!(2n+1))，在 R 上成立。',
    '(a) cₙ = n+1，故 1/(1−x)² = Σ_{n≥0} (n+1)xⁿ；(b) eˣ sin x = x + x² + x³/3 − x⁵/30 + ...，收敛半径 R=+∞。',
    '逐点极限 f=0，但 ∫₀¹ fₙ = n²/(2(n+1)) → +∞ ≠ ∫₀¹ f。由定理 3(ii) 知收敛不可能一致；事实上 Mₙ → +∞。',
]
for i, a in enumerate(zh_s2, 1):
    add_para(f'习题 {i}. {a}')

# ---- 说明性尾注 ----
doc.add_paragraph()
note = doc.add_paragraph()
r = note.add_run('注：课件中的 in-text Example（穿插在正文中的例题）多数带有完整推导过程，篇幅较长，本文件列出题目要点供查阅；若需要某道例题的完整推导，请告知编号。Unit 4 定积分部分第 6 题因原课件 OCR 识别不完整，答案暂缺，建议核对原 PDF 第 66 页。')
set_run_font(r, name_zh='楷体', size=10, color=(128, 128, 128))

# ---- 保存 ----
out_path = r'C:\Users\应轩旸\Desktop\高数课件整理_含中文答案.docx'
doc.save(out_path)
print('SAVED:', out_path)
