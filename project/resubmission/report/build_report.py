#!/usr/bin/env python3
"""Build the resubmission report from the graded docx.

    python3 build_report.py OUT.docx

Every graded element of Project_report_group6.docx is kept: text, tables, figures and equations.
The script renumbers the sections, figures and tables, corrects the scenario 3 sentence that was
wrong, and inserts the new sections with native Word equations (omml.py). Numbers come from
EVIDENCE.md.
"""

import copy
import pathlib
import sys

import docx
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.shared import Inches
from xml.sax.saxutils import escape

from omml import (CTRL, M_NS, W_NS, d, dot, frac, func, hat, math, norm2, r, rp, sub, summ, sup)

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
TEMPLATE = PROJECT / 'Project_report_group6.docx'
FIGS = HERE / 'figures'
NS = 'xmlns:w="%s" xmlns:m="%s"' % (W_NS, M_NS)
Q = ' '   # em space inside an equation (a plain space shows as a box in LibreOffice)
MINUS = '−'


def fmin(lim, body):
    return ('<m:func><m:funcPr>%s</m:funcPr><m:fName><m:limLow><m:limLowPr>%s</m:limLowPr><m:e>%s</m:e>'
            '<m:lim>%s</m:lim></m:limLow></m:fName><m:e>%s</m:e></m:func>' % (CTRL, CTRL, rp('min'), lim, body))


# ------------------------------------------------------------------ the template

doc = docx.Document(str(TEMPLATE))
body = doc.element.body
sectPr = body.find(qn('w:sectPr'))
old = [c for c in body if c.tag != qn('w:sectPr')]


def text_of(el):
    return ''.join(t.text or '' for t in el.iter(qn('w:t')))


def find(prefix):
    hits = [c for c in old if c.tag == qn('w:p') and text_of(c).strip().startswith(prefix)]
    assert len(hits) == 1, (prefix, len(hits))
    return hits[0]


def after(el):
    return old[old.index(el) + 1]


TABLES = [c for c in old if c.tag == qn('w:tbl')]
T_S2, T_S3, T_S4 = TABLES
PROTO = dict(h1=find('3. The controller'), h2=find('What we took from Lab 2'), body=find('Every 0.1 s, do-mpc'),
             eq=find('Every 0.1 s, do-mpc'), figcap=find('Figure 1:'), tabcap=find('Table 1:'),
             bullet=find('Combined demo video'), figure=after(find('Our node reads the robot')))
PROTO['eq'] = old[old.index(find('The robot is a unicycle')) + 1]


def clone_text(proto, text, italic=False):
    """A new paragraph with proto's paragraph and run formatting and the given text."""
    p = copy.deepcopy(proto)
    first_rpr = None
    for run in p.findall(qn('w:r')):
        if first_rpr is None and run.find(qn('w:rPr')) is not None:
            first_rpr = copy.deepcopy(run.find(qn('w:rPr')))
    for child in list(p):
        if child.tag != qn('w:pPr'):
            p.remove(child)
    run = parse_xml('<w:r %s>%s<w:t xml:space="preserve">%s</w:t></w:r>'
                    % (NS, '<w:rPr><w:i/></w:rPr>' if italic and first_rpr is None else '', escape(text)))
    if first_rpr is not None:
        run.insert(0, first_rpr)
    p.append(run)
    return p


def set_text(p, text):
    """Replace a paragraph's text, keeping its paragraph and first-run formatting."""
    new = clone_text(p, text)
    p.getparent().replace(p, new) if p.getparent() is not None else None
    return new


def H1(t): return clone_text(PROTO['h1'], t)
def H2(t): return clone_text(PROTO['h2'], t)
def P(t): return clone_text(PROTO['body'], t)
def TODO(t): return clone_text(PROTO['body'], '[' + t + ']', italic=True)
def BULLET(t): return clone_text(PROTO['bullet'], t)
def FIGCAP(t): return clone_text(PROTO['figcap'], t)
def TABCAP(t): return clone_text(PROTO['tabcap'], t)
def BLANK(): return parse_xml('<w:p %s/>' % NS)


def EQ(*parts):
    p = copy.deepcopy(PROTO['eq'])
    for child in list(p):
        if child.tag != qn('w:pPr'):
            p.remove(child)
    p.append(parse_xml('<w:wrap %s>%s</w:wrap>' % (NS, math(*parts)))[0])
    return p


def FIG(name, width=6.8):
    doc.add_picture(str(FIGS / name), width=Inches(width))
    p = body.findall(qn('w:p'))[-1]
    body.remove(p)
    ppr = PROTO['figure'].find(qn('w:pPr'))
    if ppr is not None:
        p.insert(0, copy.deepcopy(ppr))
    return p


def TABLE(header, rows, widths):
    """A table in the template's style: Table Grid, centred, 9 pt, grey bold header."""
    def cell(text, w, head):
        shade = '<w:shd w:val="clear" w:color="auto" w:fill="EDEDED"/>' if head else ''
        return ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s</w:tcPr><w:p><w:pPr><w:spacing w:after="0" '
                'w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:rPr>%s<w:sz w:val="18"/></w:rPr>'
                '<w:t xml:space="preserve">%s</w:t></w:r></w:p></w:tc>'
                % (w, shade, '<w:b/>' if head else '', escape(text)))
    rows_xml = ''.join('<w:tr><w:trPr><w:jc w:val="center"/></w:trPr>%s</w:tr>'
                       % ''.join(cell(c, w, i == 0) for c, w in zip(row, widths))
                       for i, row in enumerate([header] + rows))
    return parse_xml(
        '<w:tbl %s><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/>'
        '<w:tblLayout w:type="fixed"/><w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" '
        'w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>%s</w:tblGrid>%s</w:tbl>'
        % (NS, sum(widths), ''.join('<w:gridCol w:w="%d"/>' % w for w in widths), rows_xml))


# ------------------------------------------------------------------ edits to graded text

def replace_in(prefix, old_text, new_text):
    p = find(prefix)
    full = text_of(p)
    assert old_text in full, (prefix, old_text)
    new = clone_text(p, full.replace(old_text, new_text))
    old[old.index(p)] = new
    return new


def retitle(prefix, title):
    p = find(prefix)
    new = clone_text(p, title)
    old[old.index(p)] = new
    return new


E = {}   # graded elements we place, by a short name

E['title'], E['subtitle'], E['group'] = find('R7021E Advanced'), find('Project: MPC'), find('Group 6')
E['contrib_h'], E['contrib_1'], E['contrib_2'] = find('Contributions'), find('Dominic Addo (domadd-2)'), find('Abdalrahman Nasser')
E['code_h'], E['code_p'] = find('Code, bags and video'), find('The code is in the submission')
E['code_b1'], E['code_b2'] = find('Combined demo video'), find('Bags of the graded runs')
E['s1_h'], E['s1_p1'], E['q1'], E['q2'], E['s1_p2'] = (find('1. Problem and questions'), find('In Lab 2 we built'),
                                                    find('Does describing the body'), find('If the controller is told'),
                                                    find('As in the proposal, we worked'))
E['bd_h'], E['bd_p'] = find('2. Block diagram'), find('Our node reads the robot')
E['bd_fig'], E['bd_cap'] = after(E['bd_p']), find('Figure 1:')
E['lab2_p1'] = replace_in('The robot is a unicycle', 'The robot is a unicycle with state (x, y, θ) and inputs v and ω:',
                          'The robot is a unicycle. Its state is x = (x, y, θ), the position of the wheel axle and the '
                          'heading. Its input is u = (v, ω), the forward speed and the turn rate. The model is')
E['lab2_eq'] = after(find('The robot is a unicycle'))
E['lab2_p2'] = find('Every 0.1 s, do-mpc')
E['discs'] = [find('A disc gives a smooth'), after(find('A disc gives a smooth')), find('In words: the radius is half'),
              after(find('In words: the radius is half')), find('In words: every disc centre')]
E['horizon'] = [find('With N = 20 the solve fits'), find('The controller steers from odometry')]
E['mover_p1'] = find('For a moving obstacle we did')
E['mover_eq'] = after(E['mover_p1'])
E['mover_p2'] = replace_in('In words: in the "with its future"', '(section 5)', '(section 6.2)')
E['goal_p1'] = find('In scenario 4 the goal is a ball')
E['goal_eq'] = after(E['goal_p1'])
E['goal_p2'] = find('In words: v is the slope')
E['check_p1'] = find('The controller plans with discs')
E['check_eq'] = after(E['check_p1'])
E['check_p2'] = replace_in('In words: move the obstacle centre', 'every Gazebo result in section 5', 'every Gazebo result in section 6')
E['s2_p1'] = find('Scenario 2 is the main test')
E['s2_cap'] = find('Table 1:')
E['s2_blank'] = after(T_S2) if text_of(after(T_S2)).strip() == '' else None
E['s2_p2'], E['s1_p'] = find('The three-disc robot passed every gap'), find('In scenario 1 the robot follows')
E['s1_fig'], E['s1_cap'] = after(E['s1_p']), find('Figure 2:')
E['s3_p1'], E['s3_cap'] = find('Scenario 3 tests question 2'), find('Table 2:')
E['s3_blank'] = after(T_S3)
E['s3_p2'] = find('The controller that knew the obstacle')
E['s3_fig'], E['s3_figcap'], E['s3_p4'] = after(find('The robot that knew the future')), find('Figure 3:'), find('To the controller that only knew')
E['s4_p1'], E['s4_cap'] = find('Scenario 4 tests question 2 for a goal'), find('Table 3:')
E['s4_blank'] = after(T_S4)
E['s4_fig'], E['s4_figcap'], E['s4_p2'] = after(E['s4_blank']), find('Figure 4:'), find('With the fit, the robot got')
E['chg_p1'] = replace_in('Our first proposal, for a group', 'section 3 says why we added them', 'sections 3 and 4 say why we added them')
E['chg_p2'] = find("Lab 2's node did not stop")
E['lim_p1'] = replace_in('Everything here is simulation',
                         'but they are a small sample for judging the size of the gain in scenario 4.',
                         'but they are a small sample for judging the size of the gain in scenario 4. Ten more default '
                         'runs of scenario 3 with the future known, made after the presentation, all passed, with '
                         'clearances from +0.037 to +0.071 m. That is a wider spread than the three graded runs. '
                         'Seven more default runs with only the position now all touched the obstacle, by 6 to 30 mm.')
E['lim_p2'] = find('The ground truth, which the controller never sees')
E['lect_p'] = find('The controller comes from Lecture 4')

# The scenario 3 sentence that was wrong, corrected in place.
E['s3_p3'] = P(
    'The robot that knew the future stopped before the obstacle\'s path, turned clockwise on the spot to about '
    '‑90 degrees while the obstacle went past, and then drove on to the goal, which it reached in 11.4 to 11.5 s. '
    'The same drive through the open 0.60 m corridor of scenario 2 took 8.9 s. In the first version of this report '
    'we wrote that turning on the spot was the only way the controller had to pull the front of the plank back from '
    'the obstacle\'s path. That was wrong. When we made the solver turn the other way, counter-clockwise, the robot '
    'drove up and behind the obstacle and reached the goal 1.7 to 1.8 s sooner, with at least as much clearance and '
    'less turning (section 7.1). The clockwise turn on the spot is the plan our solver settles on, not the only one. Section 7.2 adds a second '
    'qualification: with a turn limit of 1.2 rad/s instead of 0.8 rad/s, the controller without the future also '
    'kept clear, by 3 to 20 mm.')

# ------------------------------------------------------------------ new content

NEW = {}

NEW['revised_line'] = clone_text(E['group'], 'Revised report after the presentation, 2 November 2026')
NEW['contrib_3'] = P('Resubmission: Dominic Addo ran the experiments in section 7 and revised the report. '
                     'Abdalrahman Nasser reviewed the revised report.')
NEW['code_b3'] = BULLET('Bags of the experiments after the presentation: [Drive link to be added]')
NEW['code_b4'] = BULLET('Screen recordings of scenarios 3 and 4 in Gazebo and RViz: [Drive link to be added]')
NEW['s1_p3'] = P('This is the revised report. After the presentation we added the full MPC problem (section 3), '
                 'the constraints and the scenario definitions (section 4), three experiments (section 7) and our '
                 'response to the feedback (section 11). Section 6.2 corrects one claim about scenario 3 that was wrong '
                 'in the first version, and section 7.2 qualifies the scenario 3 result.')

# 3.1 In words for the unicycle (the graded equation had none)
NEW['lab2_words'] = P('In words: the forward speed moves the axle along the heading, and the turn rate changes the '
                      'heading. The robot cannot move sideways.')

# 3.2 Prediction model and discretisation
NEW['pm'] = [
    P('We build the model in do-mpc as a continuous model, do_mpc.model.Model(\'continuous\'), with the three '
      'states, the two inputs and the time-varying parameters. In every scenario the parameters hold the goal g. In '
      'scenario 3 they also hold the obstacle centre o. Each parameter has one value per step of the horizon, so the '
      'solver sees a goal g_k and an obstacle centre o_k for k = 0, ..., N.'),
    P('do-mpc turns the continuous model into N = 20 steps of Δt = 0.1 s by orthogonal collocation. We read the '
      'settings from the installed do-mpc 5.1.1 instead of assuming them: Radau points, polynomial degree 2 and one '
      'finite element per step. Inside step k the state is a polynomial of degree 2 in time. It passes through the '
      'start state x_k,0 = x_k and through two collocation states x_k,1 and x_k,2, at τ_1 = 1/3 and τ_2 = 1 of the '
      'step. The model must hold at both collocation points:'),
    EQ(summ(r('r=0'), r('2'), sub(dot('ℓ'), 'r') + d(sub('τ', 'j')) + sub('x', 'k,r')),
       r('=Δt' + Q + 'f') + d(sub('x', 'k,j') + r(',') + sub('u', 'k')) + r(',' + Q + 'j=1,2,' + Q),
       sub('x', 'k+1') + r('=') + sub('x', 'k,2')),
    P('In words: ℓ_r are the Lagrange polynomials through the three points, so the left side is the slope of the '
      'state polynomial at τ_j. It must equal the unicycle model f, scaled by the step length. The input u_k is '
      'constant over the step. The last Radau point is the end of the step, so x_k,2 is where step k ends and step '
      'k + 1 starts. From here on we write the whole step as x_k+1 = F(x_k, u_k).'),
    P('The command we compute now reaches the wheels about one tick later. So the solve does not start from the '
      'measured state x_m but from where the robot will be one tick later if it keeps the last command (v⁻, ω⁻):'),
    EQ(sub(hat('x'), '0'), r('='), sub('x', 'm'), r('+Δt'),
       sup(d(sup('v', MINUS) + func('cos', sub('θ', 'm')) + r(',') + sup('v', MINUS)
             + func('sin', sub('θ', 'm')) + r(',') + sup('ω', MINUS)), 'T')),
    P('In words: one Euler step of the unicycle model with the last command sent. The parameter delay_steps sets the '
      'number of such steps. It is 1 in every run in this report.'),
]

# 3.5 Cost function
NEW['cost'] = [
    P('The cost of a plan is'),
    EQ(r('J='), summ(r('k=0'), r('N' + MINUS + '1'),
                     d(sub('q', 'p') + norm2(sub('p', 'k') + r(MINUS) + sub('g', 'k')) + r('+') + sub('r', 'u')
                       + norm2(sub('u', 'k') + r(MINUS) + sub('u', 'k' + MINUS + '1')), '[', ']')),
       r('+'), sub('q', 't'), norm2(sub('p', 'N') + r(MINUS) + sub('g', 'N')),
       r('+ρ'), summ(r('k=0'), r('N' + MINUS + '1'), summ(r('c'), None, sub('ε', 'k,c')))),
    P('In words: p_k = (x_k, y_k) is the axle position at step k. The first term pulls every step of the plan '
      'towards the goal. The second charges every change of the inputs. The third pulls the last step towards the '
      'goal once more. The last term charges every unit of slack in the soft constraints of section 4.1.'),
    P('We use q_p = q_t = 1 and r_u = 0.01 on both inputs, the Lab 2 values, and ρ = 10^4. We checked each term '
      'against the do-mpc source. The stage term is summed over k = 0 to N - 1, and the terminal term is applied '
      'once, at step N. The input change at k = 0 is measured against u_-1, the first input of the previous solve, '
      'which do-mpc keeps. The slack term is linear: do-mpc adds ρ times each slack. The stage term at k = 0 depends '
      'only on the start state, which is fixed, so it does not change the solution. The cost has no heading term, '
      'and it charges only changes of the inputs, not their size. Section 7.1 shows what the missing heading term '
      'means in scenario 3.'),
]

# 3.6 The optimisation problem
NEW['ocp'] = [
    P('At every tick the controller solves'),
    EQ(fmin(sub('u', '0') + r(',…,') + sub('u', 'N' + MINUS + '1') + r(',ε'), r('J'))),
    P('subject to, for k = 0, ..., N - 1 and every soft constraint c,'),
    EQ(sub('x', '0'), r('='), sub(hat('x'), '0'), r(',' + Q), sub('x', 'k+1'), r('=F'),
       d(sub('x', 'k') + r(',') + sub('u', 'k'))),
    EQ(r('0≤'), sub('v', 'k'), r('≤'), sub('v', 'max'), r(',' + Q + MINUS), sub('ω', 'max'),
       r('≤'), sub('ω', 'k'), r('≤'), sub('ω', 'max')),
    EQ(sub('h', 'c'), d(sub('x', 'k') + r(',') + sub('o', 'k')), r('≤'), sub('ε', 'k,c'), r(',' + Q),
       sub('ε', 'k,c'), r('≥0')),
    P('In words: find the inputs and slacks with the lowest cost, such that the plan starts at the delay-compensated '
      'state, follows the unicycle model, keeps the inputs inside their limits, and keeps every soft constraint h_c '
      'below its slack. The states at every step and collocation point are decision variables too. The model '
      'equations tie them to the inputs.'),
    P('The input bounds are hard. The soft constraints are the four sides of the box and one keep-out per disc per '
      'obstacle, listed in Table 2. do-mpc checks them at the start of each step, k = 0 to N - 1, and not at the '
      'last state x_N. At k = 0 the state is fixed. If the robot already stands inside a keep-out, the slack of that '
      'step takes the violation and the problem stays feasible. This is why we made the box soft after Lab 2.'),
    P('At every tick the controller gets the start state, the goals g_0 to g_N, the obstacle centres o_0 to o_N in '
      'scenario 3, and the previous input u_-1. It returns the planned inputs u_0 to u_N-1. We send only u_0 and '
      'solve again 0.1 s later with new measurements. This is the receding horizon.'),
]

# 3.7 Solver
NEW['solver'] = [
    P('do-mpc hands the problem to CasADi 3.7.2, which builds the derivatives and calls IPOPT 3.14.11, an interior '
      'point solver for nonlinear problems, with the linear solver MUMPS. We set three options, all to silence the '
      'output (print_level 0, sb yes, print_time 0). Every other option is the IPOPT default. Table 1 gives the size '
      'of the problem, read from the built solver.'),
    TABCAP('Table 1: Size of the optimisation problem at N = 20, read from the built solver.'),
    TABLE(['scenario', 'body', 'soft constraints per step', 'decision variables', 'constraints'],
          [['S1a, S1b', 'one disc', '5', '392', '343'],
           ['S1a, S1b', 'three discs', '7', '432', '383'],
           ['S2', 'one disc', '6', '412', '363'],
           ['S2', 'three discs', '10', '492', '443'],
           ['S3', 'three discs', '7', '432', '383'],
           ['S4', 'three discs', '4', '372', '323']],
          [1500, 1500, 2200, 1800, 1500]),
    BLANK(),
    P('In scenario 3, for example, the 432 variables are 252 state values (four points per step for 21 steps, three '
      'states each), 40 inputs and 140 slacks. The 383 constraints are 12 model equations and 7 soft constraints per '
      'step for 20 steps, and 3 for the start state.'),
    P('The first solve starts from a guess with every state at the start state and both inputs at zero. After that, '
      'do-mpc starts each solve from the previous solution as it is, together with its multipliers. It does not '
      'shift the plan by one step. If a solve fails, the node sends the last command again for up to three ticks and '
      'then stops the robot. The next solve after a failure starts from a fresh guess.'),
    P('The node runs on a 0.1 s timer in one thread. A solve that takes longer than a tick delays the next tick, and '
      'the robot keeps the last command until then. Every bag recorded after the presentation also holds the topic '
      '/mpc_stats, with the IPOPT iterations, the return status, the objective, the largest slack and how late each '
      'tick came.'),
]

# 3.10 One tick
NEW['tick'] = [
    P('Figure 2 follows one tick of the graded run s3_future_1, 3.0 s after the first command, rebuilt from the bag. '
      'Odometry put the axle at (0.620, -0.028) m with θ = -14.7°. The last command was v = 0.22 m/s and '
      'ω = -0.787 rad/s, so delay compensation moved the start state to (0.641, -0.033) m and -19.2°. The goal slots '
      'held (2.0, 0.0) at every step. The obstacle slots held its centre on its known path at x = 1.0 m, from '
      'y = 0.278 m at k = 0 to -0.322 m at k = 20. IPOPT solved the problem in 54.1 ms. The plan kept turning the '
      'plank clockwise and moved the axle only 0.12 m in the next 2 s, to (0.726, -0.114) m, so the plank stayed out '
      'of the obstacle\'s way while it passed. The node sent the first input, v = 0.22 m/s and ω = -0.794 rad/s, '
      'and solved again 0.1 s later.'),
    FIG('fig_one_tick.png', width=6.2),
    FIGCAP('Figure 2: One tick of s3_future_1 at 3.0 s, rebuilt from the bag. Left: the plank at the measured pose '
           '(grey) and at the delay-compensated start (blue), the planned axle path, and the predicted obstacle with '
           'its extra 0.03 m at steps 0, 5, 10, 15 and 20. Right: the five steps of every tick.'),
]

# 4. Constraints and scenarios
NEW['s4'] = [
    H1('4. Constraints and scenarios'),
    H2('4.1 Constraints'),
    P('Table 2 lists every constraint. c_i(x) = (x + d_i cos θ, y + d_i sin θ) is the centre of disc i, at the '
      'offset d_i along the heading. The one-disc body has one disc of r_d = 0.269 m at d = 0. The three-disc body '
      'has three discs of r_d = 0.130 m at d = -0.167, 0 and +0.167 m. The box is shrunk by s = 0.269 m, the radius '
      'the plank sweeps when it turns on the spot, so the plank fits inside it at any heading.'),
    TABCAP('Table 2: The constraints of the MPC problem, at every step k = 0 to N - 1.'),
    TABLE(['constraint', 'type', 'expression', 'per step', 'values'],
          [['speed', 'hard', '0 ≤ v_k ≤ v_max', '1', 'v_max = 0.22 m/s'],
           ['turn rate', 'hard', '-ω_max ≤ ω_k ≤ ω_max', '1', 'ω_max = 0.8 rad/s'],
           ['box', 'soft', 'x_k - (x_max - s) ≤ ε, (x_min + s) - x_k ≤ ε, and the same for y', '4',
            'box from Table 3, s = 0.269 m'],
           ['fixed obstacle', 'soft', '(r_o + r_d + m)² - ‖c_i(x_k) - o‖² ≤ ε', 'one per disc and obstacle',
            'm = 0.02 m'],
           ['moving obstacle', 'soft', '(r_o + m_o + r_d + m)² - ‖c_i(x_k) - o_k‖² ≤ ε', 'one per disc',
            'm = 0.02 m, m_o = 0.03 m'],
           ['slack', '', 'ε ≥ 0, cost ρ ε in J', 'one per soft constraint', 'ρ = 10^4']],
          [1300, 700, 4000, 1600, 2000]),
    BLANK(),
    P('Both keep-outs are squared on both sides, so the solver never takes a square root. With three discs this '
      'gives 7 soft constraints per step in scenarios 1 and 3, 10 in scenario 2 and 4 in scenario 4 (Table 1).'),
    H2('4.2 Scenarios'),
    P('Table 3 defines every scenario. All values come from the SCENARIOS table in mpc_node.py, which the node, the '
      'launch file and the grader all read. The robot always starts at (0, 0) facing +x. Figure 3 draws the '
      'scenarios at one scale. In scenario 1 we report the smallest clearance and the largest distance from the '
      'path, in scenario 2 whether the robot passed and its clearance, in scenario 3 the real clearance and the goal '
      'time, and in scenario 4 the first time within 0.2 m of the ball and the mean distance over the last 5 s.'),
    TABCAP('Table 3: The scenarios. Positions in m, velocities in m/s.'),
    TABLE(['scenario', 'goal', 'obstacles', 'box: x; y', 'pair compared', 'runs'],
          [['S1a', 'circle, r = 0.8 about (0, 0), one lap in 60 s after 8 s', 'fixed, (0, 0.62), r = 0.12',
            '-2.0 to 2.0; -2.0 to 2.0', 'one disc, three discs', '1 each'],
           ['S1b', 'figure of eight, size 0.8, one lap in 45 s after 2 s', 'fixed, (0, 0.36), r = 0.08',
            '-2.0 to 2.0; -2.0 to 2.0', 'one disc, three discs', '1 each'],
           ['S2', '(2.0, 0.0)', 'posts r = 0.10 at (1.0, ±(g/2 + 0.10)), walls at y = ±(g/2 + 0.20), '
            'g = 0.60, 0.50, 0.40, 0.34, 0.30, 0.28', '-0.5 to 2.5; between the walls', 'one disc, three discs',
            '1 per gap each'],
           ['S3', '(2.0, 0.0)', 'cylinder r = 0.10 from (1.0, 1.2) at (0, -0.30)', '-0.5 to 2.5; -1.3 to 1.3',
            'its future, only its position now', '3 each, three discs'],
           ['S4', 'ball from (1.2, -1.2) at (0.05, 0.20), seen with 0.02 noise', 'none', '-0.5 to 3.5; -2.5 to 2.5',
            'fit, hold', 'seeds 1, 2, 3 each, three discs']],
          [1150, 2350, 2550, 1500, 1500, 1050]),
    BLANK(),
    FIG('fig_scenarios.png', width=6.6),
    FIGCAP('Figure 3: The scenarios from above, at one scale. Dashed red: the box. Grey: fixed obstacles. Orange: the '
           'moving obstacle and its direction. Green: the ball and its path over 17 s. Blue: the goal or the path, '
           'and the plank at the start.'),
    H2('4.3 How the ball moves, and why it is noisy'),
    P('The ball is a green sphere of radius 0.05 m, with no collision and no gravity. A velocity plugin in Gazebo '
      'moves it at the velocity our node publishes on /target/cmd_vel, (0.05, 0.20) m/s, from the node\'s first tick. '
      'So the ball moves on a straight line from (1.2, -1.2) and starts at the same moment as the robot. Gazebo '
      'publishes its true pose on /target/pose. The grader reads that pose, but the controller does not.'),
    P('The controller sees the ball\'s position with Gaussian noise added, with a standard deviation of 0.02 m on each '
      'axis. The noise comes from a generator seeded with 1, 2 or 3, so the fit and hold runs with the same seed see '
      'the same noise. We added the noise for two reasons. Without it, two positions would give the ball\'s velocity '
      'exactly, and estimating the velocity would be trivial. And the noise stands in for the measurement noise of a '
      'real sensor. We did not test other noise levels, and we make no claim about real sensors.'),
]

# 7. Further experiments
NEW['s7'] = [
    H1('7. Further experiments after the presentation'),
    P('All runs in this section use the same Gazebo setup as section 6, headless, and are graded from ground truth '
      'with the same script. Their bags are in the second Drive folder. The graded results in section 6 are '
      'unchanged.'),
    H2('7.1 Which way the plank turns in scenario 3'),
    P('At the presentation the examiners asked why the plank in scenario 3 turns down, towards -y, which is the way '
      'the obstacle moves, and whether it should turn up instead. In every default run with the future known, '
      '13 in all (the three graded runs and ten new ones), the robot turned clockwise to about ‑90 degrees.'),
    P('The cost in section 3.5 has no heading term, so nothing in it prefers one direction. IPOPT finds a local '
      'solution, and each solve starts from the previous one. We expected that once a plan turns one way, the next '
      'solves keep it. To test the other side we added an optional cost term, which is off by default. It charges a clockwise '
      'heading while the obstacle is still above the robot:'),
    EQ(sub('J', 'ccw'), r('=J+β'), summ(r('k=0'), r('N' + MINUS + '1'),
                                            sub('s', 'k') + sup(d(func('min', d(sub('θ', 'k') + r(',0')))), '2')),
       r(',' + Q), sub('s', 'k'), r('='), frac('1', '2'),
       d(r('1+') + func('tanh', d(frac(sub('o', 'y,k') + r(MINUS) + sub('y', 'k'), r('0.05')))))),
    P('In words: a heading below zero costs β times its square, but only while the predicted obstacle centre is above '
      'the robot. Once the obstacle has passed below, s_k goes to zero and the robot can head down to the goal line '
      'again. The tanh keeps the term smooth for IPOPT.'),
    P('We tried the term first without the gate s_k. With β = 0.1 and 0.3 the robot still turned clockwise, only '
      'less far. With β = 1 it turned counter-clockwise, but it stopped 0.13 m short of the goal, because the term '
      'also charged the small downward heading it needed at the end. With the gate, β = 1 still gave a clockwise '
      'turn, to about ‑50 degrees, and β = 5 and 20 gave a counter-clockwise one. We used β = 20. Table 7 and '
      'Figure 7 compare three runs of each.'),
    TABCAP('Table 7: Scenario 3 with the future known: default against forced counter-clockwise, graded from ground '
           'truth. Turn: total absolute heading change. On the spot: time with speed below 0.02 m/s and turn rate '
           'above 0.1 rad/s.'),
    TABLE(['run', 'default: goal', 'clearance', 'turn', 'on the spot', 'forced: goal', 'clearance', 'turn',
           'on the spot'],
          [['1', '11.5 s', '+0.049 m', '3.50 rad', '1.6 s', '0.09 m short', '+0.055 m', '2.01 rad', '0.20 s'],
           ['2', '11.5 s', '+0.052 m', '3.53 rad', '1.5 s', '9.7 s', '+0.069 m', '2.14 rad', '0.03 s'],
           ['3', '11.4 s', '+0.037 m', '3.51 rad', '1.3 s', '9.7 s', '+0.063 m', '2.10 rad', '0.14 s'],
           ['longest solve', '83 to 89 ms', '', '', '', '169 to 193 ms', '', '', '']],
          [1150, 1050, 1150, 950, 1000, 1250, 1150, 950, 1000]),
    BLANK(),
    FIG('fig_wp2_turn.png', width=6.2),
    FIGCAP('Figure 7: Scenario 3, default (blue) against forced counter-clockwise (orange), three runs each. Left: '
           'heading from ground truth, and the obstacle\'s y (dashed). Right: the paths, with the plank at 3 and 4 s '
           'in run 2.'),
    P('Turning counter-clockwise was better. The robot turned up to about +50 degrees, drove up and behind the '
      'obstacle and reached the goal in 9.7 s, 1.7 to 1.8 s sooner than the default. It kept +0.055 to +0.069 m of '
      'real clearance, against +0.037 to +0.052 m, and turned about 2.1 rad in total against 3.5 rad, with almost no '
      'turning on the spot. In run 1 the node stopped when odometry put it inside the 0.05 m goal tolerance, but '
      'odometry was 0.086 m off and the ground truth was 0.09 m from the goal, so our grader does not count the goal '
      'as reached. The forced turn costs one long solve. About 2.0 s into each run, when the plan switches sides, one '
      'solve took 169 to 193 ms and 75 to 85 IPOPT iterations, and the next tick came 72 to 96 ms late.'),
    P('So the examiners were right, and the first version of this report was wrong when it said that turning on the '
      'spot was the only way. Our best explanation is that the clockwise turn is a local solution of a nonconvex '
      'problem: both directions keep the plank clear, the cost does not tell them apart early on, and the solver '
      'keeps the side it starts on. We did not prove this. Two changes might find the better side without a '
      'hand-made term: a cost on time or on progress towards the goal, or solving from both sides and keeping the '
      'cheaper plan. We did not test them.'),
    H2('7.2 What can be tuned in scenario 3'),
    P('The examiners asked which parameters we could tune to make scenario 3 work better. We counted a setting as '
      'better if it gave more real clearance, less turning and an earlier goal, and if it let the controller '
      'without the future avoid contact. We changed one parameter at a time to one value below and one above the '
      'default, with one run per value in each mode: eight parameters and 32 runs, plus a default run in each '
      'mode. Then we repeated the three most promising settings three times in each mode. Table 8 and Figure 8 '
      'show the screening, and Table 9 the repeats.'),
    TABCAP('Table 8: Screening, one run per value. Real clearance with the future known / with only the position '
           'now. Default: +0.037 to +0.052 m (three runs) / -0.007 m.'),
    TABLE(['parameter', 'default', 'lower value', 'higher value'],
          [['q_position', '1.0', '0.5: +0.049 / -0.008 m', '5.0: +0.049 / -0.005 m'],
           ['q_terminal', '1.0', '0.5: +0.053 / -0.009 m', '5.0: +0.062* / -0.007 m'],
           ['r_input', '0.01', '0.001: +0.044 / -0.006 m', '0.05: +0.052 / -0.008 m'],
           ['obstacle_penalty', '10^4', '5000: +0.047 / -0.009 m', '50000: +0.045 / -0.007 m'],
           ['safety_margin', '0.02 m', '0.0: +0.029 / -0.017 m', '0.05: +0.073 / -0.002 m'],
           ['mover_margin', '0.03 m', '0.0: +0.021 / -0.012 m', '0.05: +0.070 / -0.003 m'],
           ['delay_steps', '1', '0: +0.059 / -0.008 m', '2: +0.039 / -0.005 m'],
           ['max_angular_velocity', '0.8 rad/s', '1.2: +0.047 / +0.011 m', '2.0: +0.050 / +0.016 m']],
          [2400, 1400, 3100, 3100]),
    P('* Stopped when odometry said it was at the goal; by the ground truth it was 0.13 m short.'),
    FIG('fig_wp3_tuning.png', width=5.4),
    FIGCAP('Figure 8: Screening of scenario 3: real clearance for each parameter at the lower, default and higher '
           'value. Blue: with the future known (default: mean of three runs). Red: only the position now.'),
    P('The four cost weights did not change the verdicts. With the future known the robot passed with +0.044 to '
      '+0.062 m, and with only the position now it touched the obstacle by 5 to 9 mm. The two margins set the '
      'clearance that the controller with the future keeps: in every run it was close to the sum of the two '
      'margins, from +0.021 m with no extra margin for the moving obstacle to +0.073 m with a safety margin of '
      '0.05 m. A larger margin made the contact without the future shallower, down to 2 mm, but did not remove it. '
      'Delay compensation over 0 or 2 ticks did not change the verdicts either. Only the turn rate limit changed '
      'the result without the future.'),
    TABCAP('Table 9: The three most promising settings, three runs in each mode.'),
    TABLE(['setting', 'with the future: passed, clearance, goal', 'only the position now: contact, clearance, goal'],
          [['max_angular_velocity 1.2 rad/s', '3 of 3, +0.043 to +0.049 m, 11.1 to 11.2 s',
            'no contact in 3 of 3, +0.003 to +0.020 m, 11.7 s in 2 of 3*'],
           ['max_angular_velocity 2.0 rad/s', '3 of 3 clear, +0.047 to +0.052 m, 11.0 s in 1 of 3**',
            'no contact in 3 of 3, +0.003 to +0.021 m, 12.7 to 12.9 s in 2 of 3**'],
           ['safety_margin 0.05 m', '3 of 3, +0.075 to +0.086 m, 11.5 s in 2 of 3*',
            'contact in 3 of 3, -0.004 to -0.001 m'],
           ['default (sections 6.2, 7.1, 7.3)', '13 of 13, +0.037 to +0.071 m, 11.4 to 11.8 s',
            'contact in 10 of 10, -0.030 to -0.006 m']],
          [2600, 3600, 3800]),
    P('* The other run stopped when odometry said it was at the goal; by the ground truth it was 0.09 to 0.13 m '
      'short. ** In the other runs odometry was 0.22 to 0.89 m off the truth at the end.'),
    P('With ω_max = 1.2 rad/s the robot with the future reached the goal 0.2 to 0.4 s sooner than the default, in '
      '11.1 to 11.2 s, with the same clearance and about the same turning, 3.62 to 3.67 rad against 3.50 to '
      '3.53 rad. The controller without the future kept clear in all four runs, the screening run and three '
      'repeats, but only by 3 to 20 mm. It reached the goal in 11.7 to 12.3 s in three of them. With 2.0 rad/s '
      'odometry was 0.22 to 0.89 m off the truth in three of six runs. Our best explanation is that the wheels '
      'slip in Gazebo during the fast turns; we did not test it. A larger safety margin raised the clearance with '
      'the future known to +0.075 to +0.086 m at no cost in time, but it did not prevent contact without the '
      'future.'),
    P('This changes how we read scenario 3. In section 6.2 the controller without the future touched the obstacle '
      'in every run. That result holds at the turn limit of 0.8 rad/s that we kept from Lab 2. At 1.2 rad/s the '
      'late reaction was fast enough to keep clear, so part of the difference in the graded pair came from the turn '
      'limit and not only from knowing the future. Knowing the future still helped at 1.2 rad/s: +0.043 to '
      '+0.049 m of clearance against +0.003 to +0.020 m, and the goal 0.5 to 1.2 s sooner. Two cautions. The '
      "Burger's own limit is 2.84 rad/s (turtlebot3_teleop), so 1.2 rad/s is within it, but our model limits v "
      'and ω separately. At v = 0.22 m/s and ω = 1.2 rad/s the outer wheel would need 0.316 m/s (section 9). And '
      '3 mm is a very small clearance. The graded pair in section 6.2 stays the result at the default settings.'),
    P('Our recommended setting, as an addition, is max_angular_velocity = 1.2 rad/s with every other parameter at '
      'its default; its numbers are in Table 9. With the future known, the counter-clockwise term of section 7.1 '
      'helped more: the goal in 9.7 s with +0.055 to +0.069 m. We did not test the two together.'),
    H2('7.3 A longer or shorter horizon'),
    P('We ran scenarios 3 and 4 with N = 10, 20, 30 and 40 steps of 0.1 s, so the plan looks 1 to 4 s ahead. '
      'The problem grows with N: in scenario 3 it has 222 decision variables at N = 10 and 852 at N = 40. Each '
      'mode ran three times, and scenario 4 used the noise seeds 1, 2 and 3. N = 20 is the setting of section 6. '
      'In 10 of the 24 runs of scenario 4 the node kept running for 8 s after the end of the run. The stop signal '
      'arrived during a solve, the solver call turned it into an error, and the node caught that error and went '
      'on. So we graded every run of this section over the first 15.5 s after the first command, the normal '
      'length of a run. Over that window the graded runs of section 6.3 give the numbers of Table 6 to within '
      '1 mm. Table 10 and Figure 9 give the results.'),
    TABCAP('Table 10: Scenarios 3 and 4 against the horizon N, three runs per mode. S4: mean distance to the ball '
           'over the last 5 s, mean of three runs. Late ticks: ticks that came more than 10 ms after their slot.'),
    TABLE(['N', 'S3 future: passed, clearance', 'S3 now: contact, clearance', 'S4 fit: first within 0.2 m, mean',
           'S4 hold: mean', 'S3 median solve', 'S3 late ticks per run (future; now)'],
          [['10', '2 of 3*, +0.048 to +0.082 m', '3 of 3, -0.007 to -0.006 m', '13.9 to 15.1 s, 0.218 m',
            '0.305 m', '15 to 19 ms', '0; 0'],
           ['20', '3 of 3, +0.049 to +0.050 m', '3 of 3, -0.030 to -0.007 m', '10.4 to 14.0 s, 0.184 m',
            '0.310 m', '32 to 37 ms', '0; 2 to 4'],
           ['30', '3 of 3, +0.052 to +0.066 m', '3 of 3, -0.009 to -0.003 m', '8.6 to 12.6 s, 0.171 m',
            '0.364 m', '47 to 54 ms', '3 to 7; 4 to 9'],
           ['40', '2 of 3**, +0.045 to +0.067 m', '3 of 3, -0.023 to -0.011 m', '7.3 to 7.9 s, 0.125 m',
            '0.374 m', '62 to 73 ms', '10 to 11; 13 to 17']],
          [500, 1950, 1750, 1850, 1000, 1250, 1700]),
    P('* Kept clear, but turned on the spot for 6.7 s, more than a full turn, and did not reach the goal in the '
      'window. ** Stopped on odometry; the ground truth was 0.20 m from the goal and odometry 0.19 m off. No '
      'contact.'),
    FIG('fig_wp4_horizon.png', width=6.2),
    FIGCAP('Figure 9: Against the horizon N. Left: real clearance in scenario 3. Middle: mean distance to the ball '
           'over the last 5 s in scenario 4. Right: median solve time and late ticks per run in scenario 3.'),
    P('In scenario 3 the horizon did not change the verdicts. With the future known the robot passed in every run '
      'that reached the goal, with +0.045 to +0.082 m of clearance, and at N = 40 it reached the goal in 11.0 to '
      '11.1 s against 11.4 to 11.6 s at the other horizons. With only the position now the plank touched the '
      'obstacle in all 12 runs. A longer plan does not help here, because the obstacle stands still in it however '
      'far it looks.'),
    P('In scenario 4 the fit got better with a longer horizon. It first came within 0.2 m of the ball after 13.9 '
      'to 15.1 s at N = 10 and after 7.3 to 7.9 s at N = 40, and the mean distance over the last 5 s fell from '
      '0.218 to 0.125 m. Before the runs we expected the opposite: a longer horizon carries a slope error of the '
      'fitted line further, so the goal at the end of the plan is less certain. The data does not show that. Our '
      'best explanation is that the robot is only 7 percent faster than the ball, so seeing further along the '
      "ball's line lets it head for the point where it can catch up. The hold never came within 0.2 m, and it got "
      'slightly worse with N, from 0.305 to 0.374 m. We have no tested explanation for that.'),
    P('The cost is solve time. The median solve in scenario 3 grew from 15 to 19 ms at N = 10 to 62 to 73 ms at '
      'N = 40. From N = 30 on, late ticks appeared in scenario 3, up to 17 in one run, and single solves took up to '
      '847 ms after the contact. During a late tick the robot runs on the previous command, so at N = 40 the effect '
      'of the horizon is mixed with stale commands. The largest slack also grew, from 0.0005 at N = 20 to 0.023 at '
      'N = 40 with the future known. In scenario 4 the 95th percentile stayed below 60 ms at every N. We did not '
      'repeat the long horizons with Gazebo slowed down, which would separate the two effects. So N = 20 is still '
      'the longest horizon with no late ticks in scenario 3 with the future known, and for scenario 4 a longer '
      'horizon would have been better.'),
]

NEW['chg_p3'] = P('For the experiments in section 7 we added to the code without changing what it does by default. '
                  'A new parameter, ccw_bias, adds the heading term of section 7.1. It is 0 by default, and then the '
                  'term is not built. A new topic, /mpc_stats, publishes the solver statistics of every tick. A new launch argument, rviz, opens '
                  'RViz next to the Gazebo window for the recordings; it is off by default. With the '
                  'default parameters the controller builds the same problem as before, and new default runs of '
                  'scenario 3 gave the same verdicts as the graded runs.')
NEW['model_todo'] = [
    H2('9.1 Which model suits the plank robot'),
    P('Our controller uses the kinematic unicycle model of Lecture 4. Lecture 3 separates kinematic models, which '
      'describe motion without what causes it, from dynamic models, which include the forces and torques. A '
      'kinematic model assumes a reliable low-level motor speed controller, and Lecture 3 says kinematic control is '
      'enough when the motion is not so fast that it needs large accelerations. Our model makes four assumptions: '
      'the commanded v and ω take effect at once, with no limit on acceleration; the wheels do not slip; the plank '
      'is rigid and fixed over the axle; and v and ω are limited by two separate bounds.'),
    P('The Burger is a differential drive, and Lecture 4 gives the unicycle as its model, with v = (v_R + v_L)/2 '
      'and ω set by v_R - v_L. So the model matches the kinematics, and it allows turning on the spot, which '
      'scenario 3 uses. It does not match in three places. The Gazebo drive limits the linear acceleration to '
      '1.0 m/s², which the model does not know. After a contact in scenario 3 odometry was 1.0 to 1.6 m off the '
      'truth. Our best explanation is that the wheels did not follow the commanded motion during the contact, and '
      'the model has no way to describe that. And the two bounds on v and ω are independent, while a real robot '
      'limits each wheel.'),
    P('A differential-drive model with the wheel speeds as inputs has the same kinematics, but its limits are on '
      'each wheel, |v ± ω b/2| ≤ v_w,max, with the wheel separation b = 0.160 m. The limits are then coupled: '
      'when the robot turns fast, it must drive slower. Our two bounds allow both at once. At v = 0.22 m/s and '
      'ω = 0.8 rad/s the outer wheel moves at 0.22 + 0.8 x 0.08 = 0.284 m/s, and at ω = 2.0 rad/s at 0.38 m/s. '
      'Gazebo does not limit the wheel speed, so our runs allowed this. It matters for section 7.2, where a higher '
      'ω_max helped.'),
    P('A kinematic car model, the bicycle or Ackermann model of Lecture 3, has a steering angle and a smallest '
      'turning radius. It cannot turn on the spot. It would suit a plank on a car-like base. In scenario 3 the '
      'clockwise turn on the spot would then be impossible, and the robot would have to slow down earlier or pass '
      'behind the obstacle on a wide arc, as in the counter-clockwise runs of section 7.1.'),
    P('A dynamic model, with the velocities as states and accelerations or torques as inputs, would respect the '
      'acceleration limit. It could also describe part of the delay and of the sharp command changes that we now '
      'handle with delay compensation and the input-change cost. Lecture 3 says dynamic control is needed for fast '
      'movements and when friction, slipping or impacts matter, as in a contact. It costs at least two more states '
      'and a bigger problem to solve every 0.1 s, and section 7.3 shows how quickly the solve time grows with the '
      'size of the problem.'),
    P('Lecture 4 also shows that if the reference point is moved a distance a forward along the body, the unicycle '
      'becomes a linear system in the velocity of that point. For the plank, the front is the part that hits '
      'things, so controlling a point near the front might make the problem simpler. Our first proposal was an '
      'articulated vehicle that bends in the middle. Its shape changes with the joint angle, so the discs would '
      'move with that angle, and the model would need one more state and one more input. None of these models was '
      'tested. What we write here are expectations from the lectures and from our runs.'),
]
NEW['s11'] = [
    H1('11. Response to the feedback'),
    P('Table 11 lists every comment from the presentation, what we did about it and where it is in this report. '
      'The bags and the screen recordings are in the folders linked at the top.'),
    TABCAP('Table 11: The feedback and our response.'),
    TABLE(['comment', 'what we did', 'where'],
          [['The report is incomplete on MPC: prediction model, system dynamics, cost, minimisation problem, '
            'solver and constraints for this problem', 'Wrote the full problem with an equation and an "In words" '
            'line for each part, checked against the do-mpc source, and read the problem size from the solver',
            'Sections 3.2, 3.5 to 3.7, Table 1'],
           ['We do not understand the MPC problem you solve, or how it comes together with the solution',
            'Wrote the problem as one optimisation problem, said what goes in and out every tick, and followed '
            'one real tick from a bag', 'Sections 3.6, 3.10, Figure 2'],
           ['Add the constraints and the scenario definitions', 'One table of constraints, one of scenarios, and '
            'a figure of every scenario at one scale', 'Section 4, Tables 2 and 3, Figure 3'],
           ['In scenario 3 the robot turns down, with the obstacle. Should it not turn up?',
            'Tested. Turning up was faster, with more clearance and less turning. Our earlier claim that turning on '
            'the spot was the only way was wrong, and we corrected it', 'Sections 6.2, 7.1, Table 7, Figure 7'],
           ['What can you tune to make scenario 3 work better? Test it with a few runs',
            'Screened eight parameters and repeated the best three settings three times. A faster turn limit let the '
            'controller without the future keep clear, which weakens our scenario 3 conclusion; we say so',
            'Section 7.2, Tables 8 and 9, Figure 8'],
           ['Test the prediction horizon in scenarios 3 and 4, and send results and bags',
            'Ran N = 10 to 40, three runs per mode, with solver statistics. Bags in the second Drive folder',
            'Section 7.3, Table 10, Figure 9'],
           ['Which model other than the unicycle would suit the plank robot?', 'Text only, as agreed: four models '
            'compared with the unicycle. Not tested', 'Section 9.1'],
           ['How did the ball move, and why the Gaussian noise?', 'Described the ball and the two reasons for the '
            'noise, and what we did not test', 'Section 4.3'],
           ['Where is the Gazebo world?', 'Four screen recordings of scenarios 3 and 4, Gazebo and RViz side by '
            'side', 'Code, bags and video; Figure 3']],
          [3300, 4600, 2100]),
    BLANK(),
]

# ------------------------------------------------------------------ order

order = [
    E['title'], E['subtitle'], E['group'], NEW['revised_line'],
    E['contrib_h'], E['contrib_1'], E['contrib_2'], NEW['contrib_3'],
    E['code_h'], E['code_p'], E['code_b1'], E['code_b2'], NEW['code_b3'], NEW['code_b4'],
    E['s1_h'], E['s1_p1'], E['q1'], E['q2'], E['s1_p2'], NEW['s1_p3'],
    E['bd_h'], E['bd_p'], E['bd_fig'], E['bd_cap'],
    H1('3. The MPC problem'),
    H2('3.1 What we took from Lab 2'), E['lab2_p1'], E['lab2_eq'], NEW['lab2_words'], E['lab2_p2'],
    H2('3.2 Prediction model and discretisation'), *NEW['pm'],
    H2('3.3 The body as discs'), *E['discs'],
    H2('3.4 Horizon and safety margin'), *E['horizon'],
    H2('3.5 Cost function'), *NEW['cost'],
    H2('3.6 The optimisation problem'), *NEW['ocp'],
    H2('3.7 Solver'), *NEW['solver'],
    H2('3.8 A moving obstacle'), E['mover_p1'], E['mover_eq'], E['mover_p2'],
    H2('3.9 A moving goal'), E['goal_p1'], E['goal_eq'], E['goal_p2'],
    H2('3.10 One tick, worked through'), *NEW['tick'],
    *NEW['s4'],
    H1('5. How we check a run'), E['check_p1'], E['check_eq'], E['check_p2'],
    H1('6. Results'),
    H2('6.1 Scenarios 1 and 2: the body as discs'), E['s2_p1'], E['s2_cap'], T_S2, BLANK(), E['s2_p2'], E['s1_p'],
    E['s1_fig'], E['s1_cap'],
    H2('6.2 Scenario 3: a moving obstacle'), E['s3_p1'], E['s3_cap'], T_S3, E['s3_blank'], E['s3_p2'], E['s3_p3'],
    E['s3_fig'], E['s3_figcap'], E['s3_p4'],
    H2('6.3 Scenario 4: a moving goal'), E['s4_p1'], E['s4_cap'], T_S4, E['s4_blank'], E['s4_fig'], E['s4_figcap'],
    E['s4_p2'],
    *NEW['s7'],
    H1('8. What changed, and what did not work'), E['chg_p1'], E['chg_p2'], NEW['chg_p3'],
    H1('9. Limitations and what we learned'), E['lim_p1'], E['lim_p2'], *NEW['model_todo'],
    H1('10. Lectures and labs'), E['lect_p'],
    *NEW['s11'],
]

# Captions renumbered in order of appearance. Old: Figure 1..4, Table 1..3.
CAPTIONS = {E['bd_cap']: ('Figure 1:', 'Figure 1:'), E['s1_cap']: ('Figure 2:', 'Figure 4:'),
            E['s3_figcap']: ('Figure 3:', 'Figure 5:'), E['s4_figcap']: ('Figure 4:', 'Figure 6:'),
            E['s2_cap']: ('Table 1:', 'Table 4:'), E['s3_cap']: ('Table 2:', 'Table 5:'),
            E['s4_cap']: ('Table 3:', 'Table 6:')}
for i, el in enumerate(order):
    if el in CAPTIONS:
        a, b = CAPTIONS[el]
        order[i] = clone_text(el, text_of(el).replace(a, b, 1))

def shrink(p, factor):
    """Show a picture paragraph smaller. The picture itself is unchanged."""
    for tag in ('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent',
                '{http://schemas.openxmlformats.org/drawingml/2006/main}ext'):
        for el in p.iter(tag):
            for k in ('cx', 'cy'):
                el.set(k, str(int(int(el.get(k)) * factor)))


for key in ('s1_fig', 's3_fig', 's4_fig'):
    shrink(E[key], 0.8)

used = set(map(id, order))
dropped = [text_of(c)[:60] for c in old if id(c) not in used and text_of(c).strip()]
# Graded paragraphs we replace: the old section headings and the wrong scenario 3 paragraph.
print('graded paragraphs not placed (replaced):')
for t in dropped:
    print('   ', t)

for c in list(body):
    if c is not sectPr:
        body.remove(c)
for el in order:
    sectPr.addprevious(el)

out = sys.argv[1]
doc.save(out)
print('saved', out)
