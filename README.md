# quick-qa
python selenium library

## Planning
Normally wouldn't plan in readme but for a project of 1 this is just easier.

Core:
- driver
- element
- page
- locator
- WaitFactory
- Wait Protocol

## Some Design Options
- EventFiringWebDriver
- proxy/omposition
- decorator based
- mixins
- monkey patching

thinking mix eventdiring and mixis. Simplifies somethings and still allows fo some plugins for more behaviours down the road. 


## Driver
### Inputs
- WebDriver
- WaitFactory

### find
#### Inputs
- locator
- timeout - has default
- conditions - has default

#### Outputs
- Element
- raise ElementNotFoundException
- raise TypeError - if bad arguments


