import React from "react"

import { BasketProp, BasketCardProp, QuantityProp } from "./EpicerieProps"

const BasketPrice : React.FC<BasketProp> = (prop : BasketProp) => {
  // Display the price of the basket
  const price = prop.basket.price
  const date = new Date(prop.basket.pickup_date)
  return (
    <div className="epicerie-card-title">
      <span>
        Panier à {price / 100}€, du {date.toLocaleDateString("fr-FR")}
      </span>
    </div>
  )
}

const PrettyComposition : React.FC<BasketProp> = (prop : BasketProp) => {
  // Display the composition of the basket in a list
  const composition = prop.basket.composition
  return (
    <div className="epicerie-card-content">
      <div >
        Composition :
        </div>
      <br></br>
      <ul>
        {composition.map((vegetable, index) => (
          <li key={index}>{vegetable.name}, {vegetable.quantity}g</li>
        ))}
      </ul>
    </div>
  )
}

const QuantityButtons : React.FC<QuantityProp>  = (prop : QuantityProp) => {
  // Display the quantity of the basket and buttons to increment/decrement it
  // The data is handled in the parent component Basket
  return (
    <div className="epicerie-card-button">
      <div>
        Quantité :
      </div>
      <div>
        <button className="button blue-button" onClick={prop.quantity.decrement}>- </button>
        <span >{prop.quantity.count}</span>
        <button className="button blue-button" onClick={prop.quantity.increment}> +</button>
      </div>
    </div>
  )
}


export const Basket: React.FC<BasketCardProp> = (prop : BasketCardProp) => {
  // Basket card component
  return (
    <div className="col-sm">
      <div className="epicerie-card">
        <BasketPrice basket = {prop.basket} />
        <PrettyComposition basket = {prop.basket} />
        <QuantityButtons quantity = {prop.quantity}/>
      </div>
    </div>
  );
}