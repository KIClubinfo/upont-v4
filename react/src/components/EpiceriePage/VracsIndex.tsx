import React, {useState, useEffect, useRef} from 'react';
import { Product } from './VracCardComponents'
import { ValidationPage } from './VracValidation'

const Vracs : React.FC = () => { 

    const [vrac, setVrac] = useState(
        {
            ListProducts: [],
            pickup_date: ""
        }
    );
    const [quantities, setQuantities] = useState([]);

    const [isOrdering, setIsOrdering] = useState(false);

    const getVrac = () =>
        // @ts-ignore Urls is declared in the django template
        fetch(Urls.epicerieVracLatest())
        .then((res) => res.json())
        .then((result) => {
            // Server should return only one vrac
            setVrac(result)
            // Initialize quantities to 0
            setQuantities(new Array(result.ListProducts.length).fill(0))
        })
        .catch(console.error);

    useEffect(() => {
        getVrac();
    }
    , []);

    const incrementQuantity = (index : number, step : number, max : number) => {
        //Increment the quantity of the product at index
        setQuantities( quantities.map((quantity, i) => {
            if (i === index && quantity <= max - step) {
                return quantity + step
            } else {
                return quantity
            }
        }
        ))
    }

    const decrementQuantity = (index : number, step : number) => {
        //Decrement the quantity of the product at index, if it is > 0
        setQuantities( quantities.map((quantity, i) => {
            if (i === index && quantity >= step) {
                return quantity - step
            } else {
                return quantity
            }
        }
        ))
    }

    if (vrac.ListProducts.length === 0) {
        return (
            <div className="centered-div">
                <h1>Il n'y a pas de vrac disponible pour le moment</h1>
            </div>
        )
    }

    const handleOrderClick = () => {
        setIsOrdering(true)
    }

    if (isOrdering) {
        return (
            <ValidationPage/>
        )
    }
    return (
        <div className="vrac">
            <div className='row row-cols-5'>
                {vrac.ListProducts.map((product, index) => (
                    <Product key={index} product={product} quantity={{
                        count: quantities[index],
                        increment: () => incrementQuantity(index, product.step, product.max),
                        decrement: () => decrementQuantity(index, product.step)
                    }} />
                ))    
                }
            </div>
            <div className="centered-div">
                <button className="button blue-button" onClick={handleOrderClick}>Commander </button>
            </div>
        </div>
    );
}


export default Vracs;