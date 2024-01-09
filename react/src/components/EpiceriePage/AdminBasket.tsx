import React from "react";
import { useState, useEffect } from 'react';

const AdminBasket = () => {
    const [baskets, setBaskets] = useState([]);
    const [index, setIndex] = useState(0);

    const getBaskets = () =>
        // @ts-ignore Urls is declared in the django template
        fetch(Urls.epicerieBasketList())
            .then((res) => res.json())
            .then((result) => {
                setBaskets(result.results)
            })
            .catch(console.error);

    useEffect(() => {
        getBaskets();
    }
    , []);

    return (
        <div className="row row-cols-2">
            <div className="col-sm">
                <div className="epicerie-card">
                    <div className="epicerie-card-content">
                        Here goes the basket display
                    </div>
                </div>
            </div>
            <div className="col-sm">
                <div className="epicerie-card">
                    <div className="epicerie-card-content">
                        <div className="row">
                            <button className="button blue-button">
                                <a href="/api/epicerie/basket_orders/export" target="_blank" rel="noopener noreferrer">
                                    Exporter les commandes de paniers
                                </a>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    );
    }

export default AdminBasket;