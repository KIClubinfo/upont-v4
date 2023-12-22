import React, {useState, useEffect, useRef} from 'react';
import { Product } from './VracProductCard'
import { ValidationPage } from './VracValidation'
import { ExistingOrder } from './OrderedVrac';
import { VracOrderProp, VracOrderPreparingProp, VracProp } from './EpicerieProps';
import { DeletionPage } from './VracDeletionPage';

const Vracs : React.FC = () => { 
    // Vrac data
    const [vrac, setVrac] = useState<VracProp["vrac"] | null>(null);
    // Potential order already in the database
    const [vracOrder, setVracOrder ] = useState<VracOrderProp["vracOrder"] | null>(null);
    // Quantities input by the user
    const [quantities, setQuantities] = useState([]);
    //Is the user on the order page ?
    const [isOrdering, setIsOrdering] = useState(true);
    // Is the user on the confirmation page ?
    const [isConfirming, setIsConfirming] = useState(false);
    // Is the user about to delete the order ?
    const [isDeleting, setIsDeleting] = useState(false);


    const getData = () => 
        // We need to imbricate the fetches because we need the vrac to be loaded before the order
        // And we can't load them asynchronously because we need both to set the quantities
        // We first load the vrac - the API only returns the latest vrac
        // @ts-ignore Urls is declared in the django template
        fetch(Urls.epicerieVracLatest())
        .then((res) => res.json())
        .then((vracResult) => {
            if (vracResult.status !== "error") {
                setVrac(vracResult)
            }
            // Then we load the order - the API only returns the order for the latest vrac for the current user
            // @ts-ignore Urls is declared in the django template
            fetch(Urls.epicerieVracOrderLatestVracOrder())
            .then((res2) => res2.json())
            .then((orderResult) => {
                if (orderResult.status !== "error") {
                    setVracOrder(orderResult)
                }
                let newQuantities = new Array(vracResult.ListProducts.length).fill(0)
                if (orderResult.status !== "error") {
                    setIsOrdering(false)
                    orderResult.order.forEach((product) => {
                        const index = vracResult.ListProducts.findIndex((vracProduct) => vracProduct.id === product.id)
                        newQuantities[index] = product.quantity
                    })
                }
                setQuantities(newQuantities)
            })
            .catch(console.error);
        })

        
    // Load the data on loading the page.
    useEffect(() => {
        getData();
    }
    , []);


    const incrementQuantity = (index : number, step : number, max : number) => {
        //Increment the quantity of the product at index, if below max
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

    const handleOrderClick = () => {
        console.log(quantities)
        console.log(quantities.some( (ele) => ele > 0 ))
        if (quantities.some( (ele) => ele > 0 )) {
            setIsConfirming(true)
        }
        else if (vracOrder != null){
            setIsDeleting(true)
        }
    }

    const prepareVracOrderProp = () : VracOrderPreparingProp =>{
        // Put the quantities in the format expected by the frontend component used for the validation
        return {
            vracOrder : {
                vracId : vrac.id,
                productQuantities : vrac.ListProducts.map((product, index) => {
                    return {
                        id : product.id,
                        name : product.name,
                        price : product.price,
                        quantity : quantities[index]
                    }
                })
            }
        }
    }

    const orderButtonText = () => {
        if (vracOrder === null ) {
            return "Commander"
            } 
        else {
            return "Modifier ma commande"
            }
        }

    if (vracOrder !== null && !isOrdering) {
        return (
            <div className="vrac">
                <ExistingOrder setIsOrdering={setIsOrdering} vracOrder={vracOrder}/>
            </div>
        )
    }

    if (vrac === null || vrac.ListProducts.length === 0 ) {
        return (
            <div className="centered-div">
                <h1>Il n'y a pas de vrac disponible pour le moment</h1>
            </div>
        )
    }

    if (isDeleting) {
        return (
            <DeletionPage/>
        )
    }


    if (isConfirming) {
        return (
            <ValidationPage vracOrder = {prepareVracOrderProp()["vracOrder"]}/>
        )
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
                <button className="button blue-button" onClick={handleOrderClick}>
                    {orderButtonText()}
                </button>
            </div>
        </div>
    );
}


export default Vracs;