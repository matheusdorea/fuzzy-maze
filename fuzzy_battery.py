import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

battery = ctrl.Antecedent(np.arange(0, 101, 1), 'battery')
charger_distance = ctrl.Antecedent(np.arange(0, 21, 1), 'charger_distance')
goal_distance = ctrl.Antecedent(np.arange(0, 21, 1), 'goal_distance')
priority = ctrl.Consequent(np.arange(0, 101, 1), 'priority')

battery['low'] = fuzz.trapmf(battery.universe, [0, 0, 20, 40])
battery['medium'] = fuzz.trimf(battery.universe, [20, 50, 80])
battery['high'] = fuzz.trapmf(battery.universe, [60, 80, 100, 100])

charger_distance['near'] = fuzz.trapmf(charger_distance.universe, [0, 0, 3, 6])
charger_distance['medium'] = fuzz.trimf(charger_distance.universe, [3, 8, 13])
charger_distance['far'] = fuzz.trapmf(charger_distance.universe, [10, 15, 20, 20])

goal_distance['near'] = fuzz.trapmf(goal_distance.universe, [0, 0, 3, 6])
goal_distance['medium'] = fuzz.trimf(goal_distance.universe, [3, 8, 13])
goal_distance['far'] = fuzz.trapmf(goal_distance.universe, [10, 15, 20, 20])

priority['recharge'] = fuzz.trapmf(priority.universe, [0, 0, 30, 60])
priority['end'] = fuzz.trapmf(priority.universe, [40, 70, 100, 100])

rules = [
    ctrl.Rule(battery['low'] & charger_distance['near'], priority['recharge']),
    
    ctrl.Rule(battery['low'] & charger_distance['far'], priority['recharge']),

    ctrl.Rule(battery['medium'] & goal_distance['near'], priority['end']),

    ctrl.Rule(battery['medium'] & goal_distance['far'] & charger_distance['near'], priority['recharge']),

    ctrl.Rule(battery['medium'] & charger_distance['far'] & goal_distance['near'], priority['end']),

    ctrl.Rule(battery['high'], priority['end'])
]

priority_ctrl = ctrl.ControlSystem(rules)

def decide_goal(battery_level, distance_to_charger, distance_to_goal):
    sim = ctrl.ControlSystemSimulation(priority_ctrl)
    sim.input['battery'] = battery_level
    sim.input['charger_distance'] = distance_to_charger
    sim.input['goal_distance'] = distance_to_goal

    try:
        sim.compute()
        value = sim.output['priority']
    except Exception:
        return "recharge"

    return "recharge" if value < 50 else "end"
