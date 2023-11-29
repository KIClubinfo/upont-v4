import React from "react"

interface BasketProp {
  basket :{
    id : number
    price : number
    composition : string
    open_date : string
    close_date : string
    pickup_date : string
  }
}

const PrettyComposition : React.FC<BasketProp> = (prop : BasketProp) => {
  const composition = prop.basket.composition
  return (
    <div className="epicerie-basket-composition">
      Composition : 
      <ul>
        {composition.split("\n").map((line) => (
          <li>{line}</li>
        ))}
      </ul>
    </div>
  )
}

export const Basket: React.FC<BasketProp> = (prop : BasketProp) => (
    <div className="col-sm">
      <div className="epicerie-basket">
        <PrettyComposition basket = {prop.basket}/>
      </div>
    </div>
);