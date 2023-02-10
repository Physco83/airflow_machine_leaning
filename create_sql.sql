CREATE TABLE "category"
(category_id serial PRIMARY KEY,
parent varchar(10),
child varchar(10));


CREATE TABLE "product"
(product_id serial PRIMARY KEY,
product_name Varchar(20), 
category_id integer,
FOREIGN KEY(category_id) REFERENCES category(category_id));

CREATE TABLE "price_history"
(ph_id serial PRIMARY KEY,
date date,
price real,
sales_qty_base real,
sales_qty int,
store_location_id int,
product_id integer,
FOREIGN KEY(product_id) REFERENCES product(product_id));


CREATE TABLE "price_prediction_history"
(pph_id serial PRIMARY KEY,
date date,
price real,
product_id integer,
FOREIGN KEY(product_id) REFERENCES product(product_id));


select * from price_prediction_history limit 5;


select * from price_history ph where ph."date" >='2022-04-01' and ph."date" <='2022-04-08'


insert into price_prediction_history(pph_id, date, price, product_id) values (default, '2022-05-12', 202.2, 179553)

