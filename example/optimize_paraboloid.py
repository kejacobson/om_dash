import openmdao.api as om
import time


class Paraboloid(om.ExplicitComponent):
    def setup(self):
        self.add_input('x')
        self.add_input('y')

        self.add_output('f')

        self.declare_partials(of='f', wrt=['x', 'y'], method='fd')

    def compute(self, inputs, outputs):
        x = inputs['x']
        y = inputs['y']
        outputs['f'] = (x-3)**2 + x*y + (y+4)**2 - 3
        time.sleep(5.0)
        print('step')


# build the model
prob = om.Problem()

prob.model.add_subsystem('paraboloid', Paraboloid())

# setup the optimization
prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'

prob.model.add_design_var('paraboloid.x', lower=-50, upper=50)
prob.model.add_design_var('paraboloid.y', lower=-50, upper=50)
prob.model.add_objective('paraboloid.f')

recorder = om.SqliteRecorder("paraboloid.sql")
prob.driver.add_recorder(recorder)

prob.setup()

# Set initial values.
prob.set_val('paraboloid.x', 3.0)
prob.set_val('paraboloid.y', -4.0)

# run the optimization
prob.run_driver()
