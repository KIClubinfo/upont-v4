import ReactDOM from 'react-dom';
import React from 'react';
import { AddTransaction, LastTransactions } from '../components/shop';

ReactDOM.render(
  <>
    <AddTransaction />
    <LastTransactions />
  </>,
  window.react_mount,
);
