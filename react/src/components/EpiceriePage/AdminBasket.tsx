import React from "react";
import { useState, useEffect } from 'react';

import { BasketProp, BasketCardProp } from "./EpicerieProps"

const deleteVegetable = (id : number) => {
    // @ts-ignore Urls is declared in the django template
    fetch(Urls.epicerieVegetableDetail(id), {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then((res) => res.json())
        .then((result) => {
            console.log(result)
        })
        .catch(console.error);
}

const Composition : React.FC<BasketProp> = ( prop  : BasketProp) => {
    return (
        <div>
                <ul className="flex-list">
                    {prop.basket.composition.map((item) => (
                        <li key={item.id}>
                            {item.name} {item.quantity} g
                            <button className="button red-button"
                                onClick={() => deleteVegetable(item.id)}>
                                Supprimer
                            </button>
                        </li>
                    ))}
                </ul>
        </div>
    );
}

const AdminBasket = () => {
    const [baskets, setBaskets] = useState<BasketProp["basket"][]>([]);
    const [index, setIndex] = useState(-1);

    const getBaskets = () =>
        // @ts-ignore Urls is declared in the django template
        fetch(Urls.epicerieBasketList())
            .then((res) => res.json())
            .then((result) => {
                setBaskets(result.results)
                setIndex(0)
                console.log(result.results)
            })
            .catch(console.error);

    useEffect(() => {
        getBaskets();
    }
    , []);

    const previousBasket = () => {
        if (index < baskets.length - 1) {
            setIndex(index + 1)
        }
    }

    const nextBasket = () => {
        if (index > 0) {
            setIndex(index - 1)
        }
    }

    if (index === -1) {
        return (
            <div>
                <p>Chargement...</p>
            </div>
        );
    }

    return (
        <div className="row">
            <div className="col-8">
                <div className="epicerie-wide-box">
                    <div className="epicerie-card-title centered-div">
                        <span>
                            Panier à {baskets[index].price / 100}€ du {new Date(baskets[index].pickup_date).toLocaleDateString("fr-FR")}
                        </span>
                    </div>  
                    <div className="epicerie-card-content">
                        <Composition basket={baskets[index]} />
                    </div>

                    <div className="centered-div epicerie-card-button">
                        <div>
                            <button className="button blue-button" onClick={previousBasket}> Précédent </button>
                            <button className="button blue-button" onClick={nextBasket}> Suivant </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="col-4">
                <div className="epicerie-card">
                    <div className="epicerie-card-title">
                        <span>
                            Ajouter un panier
                        </span>
                    </div>  
                    <div className="epicerie-card-content">
                    </div>
                </div>
            </div>
                
        </div>
    );
}

export default AdminBasket;