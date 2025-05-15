# Contributing to Iris

## Testing

### Unit Tests

Unit tests for the Iris Module are managed in the Iris repository itself. This approach was selected because Slips is entirely written in Python, while Iris is based in Go. Following the best practices for unit testing in Go, it is common to integrate unit tests within the Iris repository rather than keeping them separate.

#### Important Considerations
- Currently, Go does not support mocking in the same way languages like Python or Java do. This limitation must be taken into account during unit test development.
The Slips development team has decided to leave running the unit tests for Iris to future developers, as there may be challenges due to the mocking constraints in Go.

### Running the Tests

To run the unit tests for Iris, follow these steps:
* The unit tests run best with ```go v1.17```.
* Go to the directory containing Iris code.
* ```cd pkg```
* ```go test ./...``` 
