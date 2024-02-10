## NYUPrinters

An application to help students find working printers on the NYU campus. This project started out as a way to monitor 
printers at Bobst Library for student staff. Since then, it has since grown into a full-fledged project with the
goal of monitoring printers across NYU. It comes with a secretive (not really) admin dashboard interface to manage 
printers and locations

## Design

The app is designed to be run as containers on docker or pods on kubernetes. It consists of 4 microservices: `sourced`, `statusd`, `updated`, and `store`. 
Each microservice is responsible for various tasks as shown below:

![plot](./docs/images/design.png)

## Documentation

- [API](./docs/api.md)
- [Sourced](./docs/sourced.md)
- [Statusd](./docs/statusd.md)
- [Updated](./docs/updated.md)
