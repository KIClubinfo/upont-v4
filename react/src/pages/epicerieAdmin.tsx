import { render } from 'react-dom';
import Admin from '../components/EpiceriePage/AdminIndex';

// @ts-ignore window.react_mount is declared in django template
render(<Admin />, window.react_mount);