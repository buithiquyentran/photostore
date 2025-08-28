import React, { useEffect } from 'react'
import AsssetService from '../util/photostore.api';

const Brower = () => {
  useEffect(() => {
    const fetchAssets = async () => {
      try {
        const assets = await AsssetService.GetAllAssets();
        console.log('Fetched assets:', assets);
      } catch (error) {
        console.error('Error fetching assets:', error);
      }
    }
    fetchAssets();
}, [])
  return <div className="bg-bg text-paragraph">Brower</div>;
}

export default Brower