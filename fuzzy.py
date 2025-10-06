import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

# 1. Criação das variáveis fuzzy
front = ctrl.Antecedent(np.arange(0, 201, 1), 'front')
right = ctrl.Antecedent(np.arange(0, 201, 1), 'right')
left  = ctrl.Antecedent(np.arange(0, 201, 1), 'left')
diag_right = ctrl.Antecedent(np.arange(0, 201, 1), 'diag_right')
diag_left  = ctrl.Antecedent(np.arange(0, 201, 1), 'diag_left')

speed    = ctrl.Consequent(np.arange(0, 6, 1), 'speed')

# 2. Funções de pertinência
for s in [front, right, left, diag_right, diag_left]:
    s['near']   = fuzz.trimf(s.universe, [0, 0, 50])
    s['medium'] = fuzz.trimf(s.universe, [30, 90, 150])
    s['far']    = fuzz.trimf(s.universe, [120, 200, 200])

steering = ctrl.Consequent(np.arange(-15, 16, 1), 'steering')

steering['right_strong']  = fuzz.trimf(steering.universe, [-15, -15, -8])
steering['right_slight']  = fuzz.trimf(steering.universe, [-10, -5, 0])
steering['straight']      = fuzz.trimf(steering.universe, [-3, 0, 3])
steering['left_slight']   = fuzz.trimf(steering.universe, [0, 5, 10])
steering['left_strong']   = fuzz.trimf(steering.universe, [8, 15, 15])

speed['slow'] = fuzz.trimf(speed.universe, [0, 0, 2])
speed['medium'] = fuzz.trimf(speed.universe, [1, 3, 5])
speed['fast'] = fuzz.trimf(speed.universe, [3, 5, 5])

# # 3. Regras fuzzy
# rules = []

# # Evita bater na parede frontal
# rules.append(ctrl.Rule(front['medium'], steering['left_strong']))
# rules.append(ctrl.Rule(front['far'] , steering['straight']))

# # Mantém parede direita
# rules.append(ctrl.Rule(right['near'], steering['left_slight']))

# # Ajuste com diagonais
# rules.append(ctrl.Rule(diag_right['near'] , steering['left_strong']))
# rules.append(ctrl.Rule(diag_left['near'], steering['right_strong']))
# rules.append(ctrl.Rule(diag_right['medium'] , steering['left_slight']))
# rules.append(ctrl.Rule(diag_left['medium'], steering['right_slight']))

# rules.append(ctrl.Rule(left['medium'], steering['right_slight']))

# 3. Regras fuzzy
rules = []

rules.append(ctrl.Rule(front['near'] & diag_right['near'] & diag_left['far'], steering['left_strong']))
rules.append(ctrl.Rule(front['near'] & diag_left['near'] & diag_right['far'], steering['right_strong']))

rules.append(ctrl.Rule(front['medium'] & diag_right['medium'] & diag_left['far'], steering['left_slight']))
rules.append(ctrl.Rule(front['medium'] & diag_left['medium'] & diag_right['far'], steering['right_slight']))

rules.append(ctrl.Rule(front['far'] & right['far'] & left['far'], steering['straight']))

rules.append(ctrl.Rule(front['far'] & diag_right['near'] & diag_left['far'], steering['left_strong']))
rules.append(ctrl.Rule(front['far'] & diag_right['medium'] & diag_left['far'], steering['left_slight']))
rules.append(ctrl.Rule(front['far'] & diag_right['far'] & diag_left['near'], steering['right_strong']))
rules.append(ctrl.Rule(front['far'] & diag_right['far'] & diag_left['medium'], steering['right_slight']))

rules.append(ctrl.Rule(~front['far'] & diag_left['far'] & diag_right['far'], steering['left_strong']))

rules.append(ctrl.Rule(front['near'] & diag_left['near'] & diag_right['near'], steering['left_strong']))

rules.append(ctrl.Rule(right['near'] & diag_right['far'] & diag_left['far'], steering['right_slight']))

# 4. Sistema de controle
steering_ctrl = ctrl.ControlSystem(rules)
steering_sim = ctrl.ControlSystemSimulation(steering_ctrl)

# Para usar:
# steering_sim.input['front'] = dist_front
# steering_sim.input['right'] = dist_right
# ...
# steering_sim.compute()
# steer_angle = steering_sim.output['steering']