# Maximum Take-Off Mass Optimizer (MTOMO)

QPROP is an analysis program for predicting the performance of propeller-motor or windmill-generator combinations under a specific state setpoint, snapshot in time. This script takes a run configuration that represents a plane-environment-constraints scenario and performs an optimization over the Maximum Take-Off Mass (MTOM) by forking processes executing [Mark Drela's QPROP tool](https://web.mit.edu/drela/Public/web/qprop/). If the MTOM is found, plots for $x(t)$, $v(t)$, $a(t)$, $F_T(t)$, and $F_D(t)$ are generated for the successful run as well as a performance curve over the entire optimization.

## Requirements and Running

This script was written in Python `3.13.3` and may require a version that is close to run. The script also requires that several packages be installed, which can be conveniently done by running `pip install -r requirements.txt`, assuming no virtual environment is being used for packages. By design, the script also requires a computer with at least 4 **logical processors**. The script is run using the following command:

```md
python main.py -c <config_json_path> [-p n_processes]
```

## Runs and Configurations

Each run configuration file represents a plane-environment-constraints scenario and thus the input to an optimization (run) over that scenario. The exact `json` structure of a run configuration file is shown below, where `|` delimits options. A run configuration file must consist of this exact structure.

```py
{
    "propeller_file": str,                                      # Path to propeller file
    "motor_file": str,                                          # Path to motor file
    "timestep_resolution": float | int,                         # Simulation time (s) step size
    "mass_range": [float | int, float | int],                   # Mass (kg) range to search
    "cutoff_displacement": [float | int, float | int],          # Cutoff distance (m) range
    "setpoint_parameters": {
        "velocity": None | float | int,                         # Initial velocity (m/s)
        "voltage": None | float | int,                          # Voltage (V)
        "dbeta": None | float | int,                            # Pitch-change angle (deg)
        "current": None | float | int,                          # Current (A)
        "torque": None | float | int,                           # Torque (N·m)
        "thrust": None | float | int,                           # Thrust (N)
        "pele": None | float | int,                             # Electrical Power (W)
        "rpm": None | float | int                               # RPM (rpm)
    },
    "aerodynamic_forces": {
        "fluid_density": None | float | int,                    # Fluid density (kg/m^3)
        "true_airspeed": None | float | int,                    # True airspeed (m/s)
        "drag_coefficient": None | float | int,                 # Drag coefficient
        "reference_area": None | float | int,                   # Reference area (m^2)
        "acceleration_gravity": None | float | int,             # Acceleration due to gravity (m/s^2)
        "lift_coefficient": None | float | int                  # Lift coefficient
    }
}
```

The `None` value is used to indicate to the optimizer that we don't want to provide a value ourselves, instead letting the optimizer figure it out. For `setpoint_parameters`, `None` means that the setpoint parameter should be initialized to 0. For `aerodynamic_forces`, `None` means that the parameter should be initialized to 0, except for three cases: for `acceleration_gravity` it is 9.81, for `lift_coefficient` it is 1.0, and for `true_airspeed` the optimizer should dynamically update the velocity to match the plane's current velocity at every step of the simulation.

## Example Use Case

> A plane boasts an `apc14x10e` propeller and a `CobraCM2217-26` motor. The plane must begin to take off before $100\ m$. We seek a maximum take-off mass (MTOW) so high that the plane begins to take off anytime beyond the $99\ m$ mark, but not before; this is our tolerance. The voltage at full throttle is $8.40\ V$. The plane's aerodynamic characteristics are approximated off of a similar plane to be $0.1$ for the drag coefficient, $1.0$ for the lift coefficient, and $0.075\ m^2$ for the reference area. Assume an air density of $1.225\ kg/m^3$, an acceleration due to gravity of $9.81\ m/s^2$, and variable drag. A time-step resolution of $0.1\ s$ is enough for our simulation.

For this problem, the configuration file should look something like the snippet shown below. We set `null` for `true_airspeed` to allow the optimizer to model variable drag. We could have picked a smaller mass range if we were confident about the mass range we expect the plane to be within. A tighter mass range around the MOTM also gives more meaningful graphs.

```json
{
    "propeller_file": "propeller_files/apc14x10e",
    "motor_file": "motor_files/CobraCM2217-26",
    "timestep_resolution": 0.1,
    "mass_range": [0.1, 100],
    "cutoff_displacement": [99.0, 100.0],
    "setpoint_parameters": {
        "velocity": null,
        "voltage": 8.4,
        "dbeta": null,
        "current": null,
        "torque": null,
        "thrust": null,
        "pele": null,
        "rpm": null
    },
    "aerodynamic_forces": {
        "fluid_density": 1.225,
        "true_airspeed": null,
        "drag_coefficient": 0.1,
        "reference_area": 0.075,
        "acceleration_gravity": 9.81,
        "lift_coefficient": 1.0
    }
}
```

Running the optimization with the default flags (3 worker processes) takes 8 epochs in total, around a minute (depending on your system), yielding a $v_{stall} = 10.23\ m/s$ and $m_{max} = 0.490\ kg$, as well as the dynamic analysis plots that follow. An important point is that the displacement range defines the **tolerance** that the optimization solution must satisfy. Picking a more extreme displacement range such as `[99.9, 100.0]` would indicate that we want to squeeze so much mass onto the plane as we can, to the point where we push the plane to lift off beyond $99.9\ m$ but (still) before $100.0\ m$. Though this level of (in)tolerance is clearly too extreme for most applications, it can make a difference in the solution. **Note** that before attempting this next part, set the mass range to `[0.1, 1.0]` to speed up the simulation.

<div style="text-align: center;">
    <img src='docs/readme.png' alt='Dynamic Analysis Plots' width='800' />
</div>

Attempting the extreme displacement range for the same configuration file reveals that the plane is actually capable of carrying close to $0.877\ kg$ and still taking off before $100\ m$, which is a considerable difference from the number we previously obtained! If you actually attempt a lower bound of $99.6\ m$, the simulation will quickly end with a slightly improved MTOM of $0.550\ kg$. Increase the lower bound to $99.7\ m$ and the simulation will take around 50x longer, eventually giving you the $0.877\ kg$ figure. Sometimes, as in this case, finding an MTOM within a specific tolerance given float64 precision is impossible. Even so, the result can be used, provided that the user isn't insistent on their selected tolerance. But picking a low tolerance is also risky, as you're pushing the plane's takeoff closer and closer towards the cutoff distance. In a sense, the displacement tolerance is a safety buffer. So it's a double-edged sword; you're balancing safety against capacity.

## Project Structure

This section outlines the structure of the project for documentation purposes, in case future patches must be applied.

```bash
MaximumTakeOffMassOptimizer/                    # Project root
├── components/                                 # Python script components
│   ├── utils/                                  # Python script utilities
│   │   ├── config_structure.py                 # Used to define and verify config structure
│   │   ├── process_statuses.py                 # Used to define process status enums
│   │   └── result_states.py                    # Used to define result state enums
│   ├── DynamicThrustModel.py                   # Represents a QPROP (worker) process
│   ├── ParallelBinaryOptimizer.py              # Represents the optimizer (main) process
│   └── RunConfiguration.py                     # Validates and encapsulates a run configuration
├── docs/                                       # Files referenced in documentation
│   └── readme.png                              # Image referenced in the README
├── motor_files/                                # Motor files
│   └── ...
├── propeller_files/                            # Propeller files
│   └── ...
├── .gitignore                                  # Gitignore file
├── LICENSE                                     # LICENSE file
├── main.py                                     # Main file of the script
├── qprop.exe                                   # QPROP executable dispatched by the script
├── README.md                                   # README file
└── requirements.txt                            # Package requirements file
```
