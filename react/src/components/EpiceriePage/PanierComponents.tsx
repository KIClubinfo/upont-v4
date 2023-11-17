import React from 'react';

interface Props {
  panier: {
    id: number;
    name: string;
    price: number;
    composition: string;
    pickup_time: string;
  };
}

export const Panier_Form: React.FC<Props> = (props) => (
  <div> {props.panier.name}</div>
);
