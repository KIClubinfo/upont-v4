import React, {useState, useEffect, useRef} from 'react';

import { Basket } from './BasketCard'
import { DisplayExistingOrder } from './OrderedBaskets'

const Baskets : React.FC = () => {
  
  const [baskets, setBaskets] = useState([]);
  const [orders, setOrders] = useState([]);

  const getBaskets = () =>
  // @ts-ignore Urls is declared in the django template
    fetch(Urls.epicerieBasketList())
      .then((res) => res.json())
      .then((result) => {
        setBaskets(result.results)
        setOrders(new Array(result.count).fill(0))
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
    console.log("Order clicked")
    console.log(orders)
  }

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
}

export default Baskets;