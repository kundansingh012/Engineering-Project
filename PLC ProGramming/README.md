# Demonstration Video:

https://drive.google.com/file/d/1L9ESjDdyWR5ueM1aXDrVjSyIeBBjk\_IC/view

## Challenges faced

* The push button is a momentary input. How can we use it for two inputs, like turning on and turning off the pump?
* There are only a limited number of inputs. How can we have more than 4 inputs with the current setup?
* We came up with a binary system to have more than 4 inputs, but the problem was that when you use more than one button as a single input, it can trigger something else accidentally because it is physically hard to push all the required buttons together.
* With limited knowledge of HMI and very few online videos, it was hard to design an interactive HMI that could show the tank's water level and other indicators.
* We have many ideas to implement, one of them was to have a maintenance system that can count the number of cycles of all the valves, and once the desired number is reached, it should turn on the maintenance light.
* We did not have any trouble with cylinders 1 and 4, as they had two inputs of air to close and open the cylinder, so it took us some time to figure out how to work with a cylinder with only one pneumatic input.

## Lessons learned

* We learned about the critical importance of implementing a safety system for every component.
* We also need preventive maintenance logic so that we can save a lot on unnecessary plant breakdowns.
* We developed an understanding of working with different types of pneumatic cylinders and solenoid valves and how to use them in our system.
* It is very important to have a robust PLC program that should not fail in any condition because if it fails, it can cost a lot to the plant, and it might damage the expensive components. The worst case is that it may hurt someone if our program fails to safely terminate a process because of safety issues.
  System setup images:
* All the images used in this report are from our actual setup, and we have prepared a demonstration video that shows the whole setup.
