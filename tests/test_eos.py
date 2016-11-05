# -*- coding: utf-8 -*-
'''Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2016, Caleb Bell <Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

from numpy.testing import assert_allclose
import pytest
from thermo.eos import *


@pytest.mark.sympy
def test_PR_with_sympy():
    # Test with hexane
    from sympy import  Rational, symbols, sqrt, solve, diff, integrate, N

    P, T, V = symbols('P, T, V')
    Tc = Rational('507.6')
    Pc = 3025000
    omega = Rational('0.2975')
    
    X = (-1 + (6*sqrt(2)+8)**Rational(1,3) - (6*sqrt(2)-8)**Rational(1,3))/3
    c1 = (8*(5*X+1)/(49-37*X)) # 0.45724
    c2 = (X/(X+3)) # 0.07780
    
    R = Rational('8.3144598')
    a = c1*R**2*Tc**2/Pc
    b = c2*R*Tc/Pc
    
    kappa = Rational('0.37464')+ Rational('1.54226')*omega - Rational('0.26992')*omega**2
    
    a_alpha = a*(1 + kappa*(1-sqrt(T/Tc)))**2
    PR_formula = R*T/(V-b) - a_alpha/(V*(V+b)+b*(V-b)) - P
    
    
    
    # First test - volume, liquid
    
    T_l, P_l = 299, 1000000
    PR_obj_l = PR(T=T_l, P=P_l, Tc=507.6, Pc=3025000, omega=0.2975)
#    solns = solve(PR_formula.subs({T: T_l, P:P_l}))
#    solns = [N(i) for i in solns]
#    V_l_sympy = float([i for i in solns if i.is_real][0])
    V_l_sympy = 0.00013022208100139964

    assert_allclose(PR_obj_l.V_l, V_l_sympy)

    def numeric_sub_l(expr):
        return float(expr.subs({T: T_l, P:P_l, V:PR_obj_l.V_l}))

    # First derivatives
    dP_dT = diff(PR_formula, T)
    assert_allclose(numeric_sub_l(dP_dT), PR_obj_l.dP_dT_l)

    dP_dV = diff(PR_formula, V)
    assert_allclose(numeric_sub_l(dP_dV), PR_obj_l.dP_dV_l)
    
    dV_dT = -diff(PR_formula, T)/diff(PR_formula, V)
    assert_allclose(numeric_sub_l(dV_dT), PR_obj_l.dV_dT_l)
    
    dV_dP = -dV_dT/diff(PR_formula, T)
    assert_allclose(numeric_sub_l(dV_dP), PR_obj_l.dV_dP_l)
    
    # Checks out with solve as well
    dT_dV = 1/dV_dT
    assert_allclose(numeric_sub_l(dT_dV), PR_obj_l.dT_dV_l)
    
    dT_dP = 1/dP_dT
    assert_allclose(numeric_sub_l(dT_dP), PR_obj_l.dT_dP_l)
    
    # Second derivatives of one variable
    d2P_dT2 = diff(dP_dT, T)
    assert_allclose(numeric_sub_l(d2P_dT2), PR_obj_l.d2P_dT2_l)
    d2P_dT2_maple = -506.20125231401374
    assert_allclose(d2P_dT2_maple, PR_obj_l.d2P_dT2_l)

    d2P_dV2 = diff(dP_dV, V)
    assert_allclose(numeric_sub_l(d2P_dV2), PR_obj_l.d2P_dV2_l)
    d2P_dV2_maple = 4.482165856521206e+17
    assert_allclose(d2P_dV2_maple, PR_obj_l.d2P_dV2_l)
    
    
    d2P_dTdV = diff(dP_dT, V)
    assert_allclose(numeric_sub_l(d2P_dTdV), PR_obj_l.d2P_dTdV_l)
    
    d2P_dTdV = diff(dP_dV, T)
    assert_allclose(numeric_sub_l(d2P_dTdV), PR_obj_l.d2P_dTdV_l)
    
    

#    d2V_dT2 = diff(dV_dT, T)
#    assert_allclose(numeric_sub_l(d2V_dT2), PR_obj_l.d2V_dT2_l)
#    d2V_dT2_maple = 1.168851368E-9
#    
#    d2V_dP2 = diff(dV_dP, P)
#    assert_allclose(numeric_sub_l(d2V_dP2), PR_obj_l.d2V_dP2_l)
#    d2V_dP2_maple = 9.103361314E-21
    
#    d2T_dP2 = diff(dT_dP, P)
#    assert_allclose(numeric_sub_l(d2T_dP2), PR_obj_l.d2T_dP2_l)
#    d2T_dP2_maple = 2.564684443971313e-15
#    assert_allclose(d2T_dP2_maple, PR_obj_l.d2T_dP2_l)
#    
    
#    d2T_dV2_maple = -291578941281.8895
    
def test_PR_quick():
    # Test solution for molar volumes
    eos = PR(Tc=507.6, Pc=3025000, omega=0.2975, T=299., P=1E6)
    Vs_fast = eos.volume_solutions(299, 1E6, eos.b, eos.a_alpha)
    Vs_slow = eos.volume_solutions(299, 1E6, eos.b, eos.a_alpha, quick=False)
    Vs_expected = [(0.00013022208100139953-0j), (0.001123630932618011+0.0012926962852843173j), (0.001123630932618011-0.0012926962852843173j)]
    assert_allclose(Vs_fast, Vs_expected)
    assert_allclose(Vs_slow, Vs_expected)
    
    # Test of a_alphas
    a_alphas = [3.801259426590328, -0.006647926028616357, 1.6930127618563258e-05]
    eos.set_a_alpha_and_derivatives(299)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    eos.set_a_alpha_and_derivatives(299, quick=False)
    a_alphas_fast = [eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2]
    assert_allclose(a_alphas, a_alphas_fast)
    
    # PR back calculation for T
    eos = PR(Tc=507.6, Pc=3025000, omega=0.2975, V=0.00013022208100139953, P=1E6)
    assert_allclose(eos.T, 299)
    T_slow = eos.solve_T(P=1E6, V=0.00013022208100139953, quick=False)
    assert_allclose(T_slow, 299)
    
    # First derivatives
    diffs = eos.first_derivatives(eos.T, eos.V_l, eos.b, eos.a_alpha, eos.da_alpha_dT, eos.da_alpha_dT)
    diffs_expect = [582232.4757941157, -3665180614672.2373, 1.588550570914177e-07, -2.7283785033590384e-13, 6295046.681608136, 1.717527004374129e-06]
    assert_allclose(diffs, diffs_expect)
    (diffs_fast, _, _, _) = eos.derivatives_and_departures(eos.T, eos.P, eos.V_l, eos.b, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2)
    assert_allclose(diffs_fast, diffs_expect)
    
    # Second derivatives
    diff2 = eos.second_derivatives(eos.T, eos.V_l, eos.b, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2)
    diff2_expect = [-506.20125231401386, 4.482165856521269e+17]
    assert_allclose(diff2_expect, diff2)
    assert_allclose(diff2_expect, [eos.d2P_dT2_l, eos.d2P_dV2_l])
    
    # Mixed second derivatives
    second_expect = [0, -20523303691.11546, 0]
    second_slow = eos.second_derivatives_mixed(eos.T, eos.V_l, eos.b, eos.a_alpha, eos.da_alpha_dT)
    assert_allclose(second_expect, second_slow)
    second_fast = [eos.d2V_dPdT_l, eos.d2P_dTdV_l, eos.d2T_dPdV_l]
    assert_allclose(second_expect, second_fast)
    
    # Exception tests
    a = CUBIC_EOS()
    with pytest.raises(Exception):
        a.solve_T(P=1E6, V=0.001)
        
    with pytest.raises(Exception):
        a.set_a_alpha_and_derivatives(T=300)
        
    with pytest.raises(Exception):
        PR(Tc=507.6, Pc=3025000, omega=0.2975, T=299)
    
    # Integration tests
    eos = PR(Tc=507.6, Pc=3025000, omega=0.2975, T=299.,V=0.00013)
    fast_vars = vars(eos)
    eos.set_properties_from_solution(eos.T, eos.P, eos.V, eos.b, eos.a_alpha, eos.da_alpha_dT, eos.d2a_alpha_dT2, quick=False)
    slow_vars = vars(eos)
    [assert_allclose(slow_vars[i], j) for (i, j) in fast_vars.items() if isinstance(j, float)]

    # One gas phase property
    assert 'g' == PR(Tc=507.6, Pc=3025000, omega=0.2975, T=499.,P=1E5).phase


#test_PR_with_sympy()
test_PR_quick()