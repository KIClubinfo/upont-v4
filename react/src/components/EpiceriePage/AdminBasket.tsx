import React from "react";

const AdminBasket = () => {
    return (
        <div className="row row-cols-3">
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