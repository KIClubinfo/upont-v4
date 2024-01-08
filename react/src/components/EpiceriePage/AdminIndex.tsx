import React from "react";

const ExportBasketOrders = () => {

}

const Admin = () => {
    return (
        <div className="col-sm">
            <div className="epicerie-card">
                <div className="epicerie-card-content">
                    <div className="row">
                        <button className="button blue-button">
                            Modifier les paniers
                        </button>
                    </div>
                    <div className="row">
                        <button className="button blue-button">
                            Modifier le vrac
                        </button>
                    </div>
                    <div className="row">
                        <button className="button blue-button">
                            <a href="/api/epicerie/basket_orders/export" target="_blank" rel="noopener noreferrer">
                                Exporter les commandes de paniers
                            </a>
                        </button>
                    </div>
                    <div className="row">
                        <button className="button blue-button">
                            <a href="/api/epicerie/vrac_orders/export" target="_blank" rel="noopener noreferrer">
                                Exporter les commandes de vrac
                            </a>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
    }

export default Admin;