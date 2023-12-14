import React, {useState, useEffect, useRef} from 'react';
import { Product } from './VracCardComponents'

const Vracs : React.FC = () => { 
    const [vrac, setVrac] = useState(
        {
            ListProducts: [],
            pickup_date: ""
        }
    );
    const [quantities, setQuantities] = useState([]);

    const getVrac = () =>
        // @ts-ignore Urls is declared in the django template
        fetch(Urls.epicerieVracLatest())
        .then((res) => res.json())
        .then((result) => {
            // Server should return only one vrac
            console.log(result)
            setVrac(result)
            // Initialize quantities to 0
            setQuantities(new Array(result.ListProducts.length).fill(0))
        })
        .catch(console.error);

    useEffect(() => {
        // @ts-ignore Urls is declared in the django template
        console.log(Urls)
        getVrac();
    }
    , []);

    const incrementQuantity = (index : number, step : number) => {
        //Increment the quantity of the product at index
        setQuantities( quantities.map((quantity, i) => {
            if (i === index) {
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

    return (
        <div>
            {vrac.ListProducts
            .map(
                (product, index) => (
                    <Product
                    key={index} 
                    product={product} 
                    quantity={{count: quantities[index], 
                                increment: () => incrementQuantity(index, product.step), 
                                decrement: () => decrementQuantity(index, product.step)}}
                    />
                ))}
        </div>
    );
}


export default Vracs;