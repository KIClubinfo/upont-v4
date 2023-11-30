import React from 'react';

import { Basket } from './BasketComponents'

const baskets = [
  {
    id: 1,
    price : 600,
    composition : [
      "400g de carottes",
      "200g d'oignons/échalottes",
      "500g patate douce",
      "500g Pdt Allians grenaille",
      "1 poireau",
      "1 poivron long vert"
    ],
    open_date : "2023-01-01",
    close_date : "2023-01-01",
    pickup_date : "2023-01-01",
  },
  {
    id: 2,
    price : 1000,
    composition : [
      "Panier à 6€",
      "1/2 botte de persil",
      "800g courge musquée de provence",
      "1/2 chou vert",

    ],
    open_date : "2020-01-01",
    close_date : "2020-01-01",
    pickup_date : "2020-01-01",
  },
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