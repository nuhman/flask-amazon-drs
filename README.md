## Python Flask app for Amazon DRS
  
Read more about:  
* [Amazon DRS](https://developer.amazon.com/dash-replenishment-service)  
* [Flask](https://flask.pocoo.org/) - [tutorial](https://medium.com/python-pandemonium/build-simple-restful-api-with-python-and-flask-part-1-fae9ff66a706)
* [Python](https://www.learnpython.org/)  
  
**Sample Services**:  
  
* register new users here:
  `https://iot2100.herokuapp.com/auth/login`
  
* replenish: GET Request  
  `https://iot2100.herokuapp.com/replenish/{user_id}/{slot_id}`  
  
  *example*: `https://iot2100.herokuapp.com/replenish/1/490d109f-23a8-476a-8f8d-0814cc3799ef`

* cancel_order: GET Request  
  `https://iot2100.herokuapp.com/cancel-order/{user_id}/{slot_id}`  
    
  *example*: `https://iot2100.herokuapp.com/cancel-order/1/490d109f-23a8-476a-8f8d-0814cc3799ef`  
  
* order_status: GET Request  
  `https://iot2100.herokuapp.com/order-status/{user_id}/{instance_id}`  
    
  *example*: `https://iot2100.herokuapp.com/orderstatus/1/amzn1.dash.v2.o.ci40MGM2ZTAyYi1kM2RhLTRhNjEtYjJhZS1kOTZjNjI4MTYyZTguZWJkZGY3ZmMtYjgxMC00MjVhLTg0YTYtMjQ4NWY3MWYxYWJm`
