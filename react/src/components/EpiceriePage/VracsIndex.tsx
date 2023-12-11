import React, {useState, useEffect, useRef} from 'react';
import { Vrac } from './VracCardComponents'

const Vracs : React.FC = () => { 
    const [vracs, setVracs] = useState([]);
    const [quantities, setQuantities] = useState([]);

    const getVracs = () =>
  // @ts-ignore Urls is declared in the django template
    fetch(Urls.epicerieVracList())
      .then((res) => res.json())
      .then((result) => {
        setVracs(result.results)
      })
      .catch(console.error);
  
  useEffect(() => {
    getVracs();

  }, []);

  const incrementQuantityCount = (event : Event , step : number) => {
    //Increment the order count of the basket at index
    setQuantities(quantities.map((quantity, i) => {
      if (i === step) {
        return quantity + step
      } else {
        return quantity
      }
    }
    ))
  };

  const decrementQuantityCount = (event : Event , step : number) => {
    //Increment the order count of the basket at index
    setQuantities(quantities.map((quantity, i) => {
      if (i === step) {
        return quantity - step
      } else {
        return quantity
      }
    }
    ))
  };

  const handleQuantityClick = () => {
    console.log("Quantity clicked")
    console.log(quantities)
  }
  return (
    <div>
      <div className="row">
        {vracs
          .map(
            (vrac, index) => (
                <Vrac vrac={vrac} key={index} quantity ={{
                  count: quantities[index],
                  increment: (event : Event) => incrementQuantityCount(event, index),
                  decrement: (event : Event) => decrementQuantityCount(event, index)
                }}/>
          ))
        }
      </div>
      <div className="centered-div">
      <button className="button blue-button" onClick={handleQuantityClick}>Commander </button>
      </div>
    </div>
  );
}


export default Vracs;