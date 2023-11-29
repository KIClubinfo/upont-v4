import React from 'react';

import { Basket } from './BasketComponents'

const baskets = [
  {
    id: 1,
    price : 100,
    composition : "Vincent \n Boulard \n et son gros cerveau",
    open_date : "2020-01-01",
    close_date : "2020-01-01",
    pickup_date : "2020-01-01",
  },
  {
    id: 2,
    price : 200,
    composition : "Nique \n la \n PEP",
    open_date : "2023-01-01",
    close_date : "2023-01-01",
    pickup_date : "2023-01-01",
  },
  // {
  //   id: 3,
  //   price : 300,
  //   composition : "Nique \n la \n PEP",
  //   open_date : "2023-01-01",
  //   close_date : "2023-01-01",
  //   pickup_date : "2023-01-01",
  // }

]

class Baskets extends React.Component {
  //Create an example instance of props

  render() {
    return (
      <div>
        <div className="row">
          {baskets.map((basket) => (
            <Basket basket={basket} key={basket.id} />
          ))}
        </div>
        <div className="centered-div">
          <button className="button blue-button">Commander </button>
        </div>
      </div>
    );
  }
}

export default Baskets;