import React, { useCallback } from 'react';
import PropTypes from 'prop-types';

const VALID_FIRST = /^[1-9]{1}$/;
const VALID_NEXT = /^[0-9]{1}$/;
const DELETE_KEY_CODE = 8;

export default function CurrencyInput({
  className,
  max,
  onValueChange,
  style,
  name,
  value,
  id,
  type,
}) {
  const valueAbsTrunc = Math.trunc(Math.abs(value));
  if (
    value !== valueAbsTrunc ||
    !Number.isFinite(value) ||
    Number.isNaN(value)
  ) {
    throw new Error(`invalid value property`);
  }

  const handleKeyDown = useCallback(
    (event) => {
      const { key, keyCode } = event;
      if (
        (value === 0 && !VALID_FIRST.test(key)) ||
        (value !== 0 && !VALID_NEXT.test(key) && keyCode !== DELETE_KEY_CODE)
      ) {
        return;
      }
      const valueString = value.toString();
      let nextValue;
      if (keyCode !== DELETE_KEY_CODE) {
        const nextValueString = value === 0 ? key : `${valueString}${key}`;
        nextValue = Number.parseInt(nextValueString, 10);
      } else {
        const nextValueString = valueString.slice(0, -1);
        nextValue =
          nextValueString === '' ? 0 : Number.parseInt(nextValueString, 10);
      }
      if (nextValue > max) {
        return;
      }
      onValueChange(nextValue);
    },
    [max, onValueChange, value],
  );

  const handleChange = useCallback(() => {
    // DUMMY TO AVOID REACT WARNING
  }, []);

  const valueDisplay = (value / 100).toLocaleString('fr-FR', {
    style: 'currency',
    currency: 'EUR',
  });

  return (
    <input
      className={className}
      inputMode="numeric"
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      style={style}
      value={valueDisplay}
      type={type}
      name={name}
      id={id}
    />
  );
}
CurrencyInput.propTypes = {
  className: PropTypes.string,
  max: PropTypes.number,
  onValueChange: PropTypes.func.isRequired,
  style: PropTypes.shape({}),
  name: PropTypes.string,
  value: PropTypes.number.isRequired,
  id: PropTypes.string,
  type: PropTypes.string,
};

CurrencyInput.defaultProps = {
  className: '',
  max: Number.MAX_SAFE_INTEGER,
  style: {},
  name: '',
  id: '',
  type: '',
};
