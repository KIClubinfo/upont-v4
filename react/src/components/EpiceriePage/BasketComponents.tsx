import React from 'react';

interface Props {
  basket: {
    price: number;
    composition: string;
    open_date : string;
    close_date : string;
    pickup_date : string;
  };
}

function BasketItem(props) {
    return (
        <div className="basket-item">
        <p>{props.price}</p>
        </div>
    );
    }


class Baskets extends React.Component {
  render() {
    return (
      <div className="basket">
            <BasketItem price="1.00€" />
      </div>
    );
  }
}

export default Baskets;