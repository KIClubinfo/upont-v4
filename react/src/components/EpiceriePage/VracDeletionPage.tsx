import React from "react";

export const DeletionPage : React.FC = () => {

    const handleCancel  = () => {
        window.location.reload();
    }

    return (
        <div className="col-sm">
            <div className="epicerie-card">
                <div className="epicerie-card-title">
                    Tu t'apprêtes à supprimer ta commande.
                    <br/>
                    Es-tu-sûr ?
                </div>
                <div className="epicerie-card-confirmation">
                    <div className="row">
                        <div className="col">
                            <button className="button red-button"
                            onClick={handleCancel}>
                                Annuler
                            </button>
                        </div>
                        <div className="col">
                            <button className="button green-button">
                                Supprimer
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    )
}