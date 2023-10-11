import React from "react";

function apartmentName(state) {
    return (
        <div className="coloc-name">
        <h2>{state.apartment.name}</h2>
        </div>
    );
}

function apartmentIllustration(state) {
    return (
        <div className="coloc-illustration">
            <img src={state.apartment.illustration} alt="coloc illustration" />
        </div>
    );
}

class Apartment extends React.Component {
    render() {
        return (
            <div className="coloc">
                {apartmentName(this.state)}
                {apartmentIllustration(this.state)}
            </div>
        );
    }
}

class Apartments extends React.Component {
    render() {
        return (
            <div className="colocs">
                {this.state.apartments.map((apartment, index) => (
                    <Apartment key={index} apartment={apartment} />
                ))}
            </div>
        );
    }
}

export default Apartments;