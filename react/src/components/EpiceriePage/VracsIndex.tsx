import React, {useState, useEffect, useRef} from 'react';
import { Product } from './VracCardComponents'
import { ValidationPage } from './VracValidation'
import { ExistingOrder } from './DispayOrderedVrac'

const Vracs : React.FC = () => { 
    //Bool to tell if the user has already ordered a vrac
    const [hasOrdered, sethasOrdered] = useState(false)
    // Vrac data
    const [vrac, setVrac] = useState(
        {
            id : 1,
            ListProducts: [
                {
                    id: 1,
                    name : "",
                    price : 0,
                    step : 1,
                    max : 1,
                }
            ],
            pickup_date: "",
        }
    );
    // Quantities input by the user
    const [quantities, setQuantities] = useState([]);
    //Is the user on the confirmation page ?
    const [isOrdering, setIsOrdering] = useState(false);

    const getHasOrdered = () => 
        // @ts-ignore Urls
        fetch(Urls.epicerieVracOrderHasOrdered())
        .then((res) => res.json())
        .then((result) => {
            sethasOrdered(result)
        }
        )
        .catch(console.error);

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
    // Load the data on loading the page.
    useEffect(() => {
        // @ts-ignore Urls 
        console.log(Urls)
        getHasOrdered();
        getVrac();
    }
    , []);

    if (hasOrdered) {
        return 
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

    const prepareVracOrderProp = () => {
        let data = { 
            id : vrac.id,
            quantityList: vrac.ListProducts.map(
                (product, index) => {
                    return (
                        {
                            id : product.id,
                            name : product.name,
                            price : product.price,
                            quantity : quantities[index],

                        }
                    )
                }
            )
        }
        return data
    }


    if (isOrdering) {
        return (
            <ValidationPage vrac = {prepareVracOrderProp()}/>
        )
    }

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
    // If we are here, the user isn't ordering, there is an available vrac and the user is sure they want to order a new v
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