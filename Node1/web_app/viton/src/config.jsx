import { useEffect, useState } from 'react';

const useConfig = () => {
    const [config, setConfig] = useState(null);

    useEffect(() => {
        fetch('/config.json')
            .then(response => response.json())
            .then(data => {
                const config = {
                    webUrl: `https://${data.IP_MAIN}:${data.webPort}`,
                    apiUrl: `https://${data.IP_MAIN}:${data.apiPort}`,
                    cameraUrl: `https://${data.IP_MAIN}:${data.cameraPort}/video_feed`
                };
                setConfig(config);
            })
            .catch(error => console.error('Error loading configuration:', error));
    }, []);

    return config;
};

export default useConfig;
