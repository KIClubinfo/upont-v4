import React, {useState, useEffect} from 'react';

import { Basket } from './BasketCard'
import { DisplayExistingOrder } from './OrderedBaskets'
import { BasketValidation } from './BasketValidation'

import { BasketProp, QuantityProp, BasketOrdersProp } from './EpicerieProps';

const Baskets : React.FC = () => {
  const [isValidationPage, setIsValidationPage] = useState(false);
  const [baskets, setBaskets] = useState<BasketProp["basket"][]>([]);
  const [orders, setOrders] = useState([]);

  const getBaskets = () =>
  // @ts-ignore Urls is declared in the django template
    fetch(Urls.epicerieBasketActive())
      .then((res) => res.json())
      .then((result) => {
        setBaskets(result)
        setOrders(new Array(result.length).fill(0))
      })
      .catch(console.error);
  
  useEffect(() => {
    getBaskets();

  }, []);

  const incrementOrderCount = (index : number) => {
    //Increment the order count of the basket at index
    setOrders( orders.map((order, i) => {
      if (i === index) {
        return order + 1
      } else {
        return order
      }
    }
    ))
  };

  const decrementOrderCount = (index : number) => {
    //Decrement the order count of the basket at index, if it is > 0
    setOrders( orders.map((order, i) => {
      if (i === index && order > 0) {
        return order - 1
      } else {
        return order
      }
    }
    ))
  };

  const handleOrderClick = () => {
    if (!orders.every(item => item === 0)) {
      setIsValidationPage(true);
    }
  };

  const prepareOrderConfirmationList = () => {
    // Prepare the list of orders to be sent to the backend
    return orders.map((order, index) => {
      if (order > 0) {
        return {
          quantity: order,
          basket: {
            id: baskets[index].id,
            price: baskets[index].price,
            pickup_date: baskets[index].pickup_date
          }
        }
      }
    }).filter(item => item !== undefined)
  }

  if (!isValidationPage) {
    return (
      <div>
        <div className="row">
          {baskets
            .sort( (a, b) => a.price - b.price)
            .map(
              (basket, index) => (
                <Basket basket={basket} key={index} quantity={{
                  count: orders[index],
                  increment: () => incrementOrderCount(index),
                  decrement: () => decrementOrderCount(index)
              }}/>
            ))
          }
          <DisplayExistingOrder />
        </div>
        <div className="centered-div">
          <button className="button blue-button" onClick={handleOrderClick}>Commander </button>
        </div>
      </div>
    );
  } else {
    return (
      <div>
        <BasketValidation orders={prepareOrderConfirmationList()}/>
      </div>
    )
  }

}

export default Baskets;