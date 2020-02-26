# Robopy

This is a programming game, where the goal is to develop a battle tank robot to battle against other tanks in Python. The robot battles run in real-time and on-screen.

Robopy is a translation of [Robocode](https://robocode.sourceforge.io) (Java to Python) aimed to be a Python version with few upgrades.

## Main Issues/Discussion Topics

### Design

- Distinction between advanced robots and basic robots has not been implemented (e.g. classes or aiming aid).

### Geometry

- The scan arc is not implemented as an arc, it's actually a polygon with 3 points (usually a triangle) because shapely doesn't have an arc object.

### Rendering

- There's no UI, opencv has been used to render battle samples during development.

### Score

- The scoring system wasn't implemented yet.

### Trigonometry

- The unusual trigonometry implemented (clockwise with 0º on top) may cause user misunderstanding and stress. It should be replaced by the normal trigonometry so they can use functions such as cos, sin, atan as they usually learn to.

## Authors

- **Thalles Medrado** - [tysm](https://github.com/tysm).

See also the list of [contributors](https://github.com/tysm/robopy/graphs/contributors) who participated in this project.
