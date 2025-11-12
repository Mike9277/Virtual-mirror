import React, { useState, useRef, useEffect } from 'react';
import { css } from '@emotion/react';
import { ClipLoader } from 'react-spinners';
import { saveAs } from 'file-saver';
import useConfig from './config';
import './css/viton.css';

export default function Camera() {
    const config = useConfig();
    const videoRef = useRef(null);
    const canvasRef = useRef(null);

    const [streamActive, setStreamActive] = useState(false);
    const [resultImageUrl, setResultImageUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [cameraError, setCameraError] = useState(null);

    // Start/stop webcam
    useEffect(() => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setCameraError("Your browser does not support camera access. Use a modern browser on localhost or HTTPS.");
            return;
        }

        if (streamActive) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    videoRef.current.srcObject = stream;
                    setCameraError(null);
                })
                .catch(err => {
                    console.error("Cannot access webcam:", err);
                    setCameraError(err.message || "Unable to access camera");
                    setStreamActive(false);
                });
        } else if (videoRef.current?.srcObject) {
            videoRef.current.srcObject.getTracks().forEach(track => track.stop());
        }
    }, [streamActive]);

    const toggleCamera = () => {
        setStreamActive(!streamActive);
        setResultImageUrl(null);
    };

    const captureImage = async () => {
        if (!videoRef.current) return;
        setLoading(true);

        const canvas = canvasRef.current;
        canvas.width = videoRef.current.videoWidth || 640;
        canvas.height = videoRef.current.videoHeight || 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL('image/jpeg');

        try {
            const response = await fetch(`${config.apiUrl}/preprocess-img`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageData, filename: 'webcam_image.jpg' })
            });

            const data = await response.json();
            if (data.original_image) {
                setResultImageUrl(`data:image/jpeg;base64,${data.original_image}`);
            } else if (data.error) {
                setCameraError(data.error);
            }
        } catch (err) {
            console.error("Error sending image to server:", err);
            setCameraError(err.message || "Error sending image to server");
        } finally {
            setLoading(false);
        }
    };

    const downloadImage = () => {
        if (!resultImageUrl) return;
        const now = new Date();
        const timestamp = `${now.getHours()}${now.getMinutes()}${now.getSeconds()}`;
        saveAs(resultImageUrl, `VITON_capture_${timestamp}.jpg`);
    };

    const override = css`
    display: block;
    margin: 0 auto;
    border-color: red;
  `;

    return (
        <div className="camera">
            <h3>Camera Capture</h3>

            {cameraError && <p style={{ color: 'red' }}>{cameraError}</p>}

            <button className="bouton_capture" onClick={toggleCamera}>
                {streamActive ? "Close Camera" : "Open Camera"}
            </button>

            {streamActive && (
                <div className="camera_live">
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        style={{ width: '640px', height: '480px', border: '1px solid #ccc' }}
                    />
                </div>
            )}

            <button
                className="bouton_capture"
                onClick={captureImage}
                disabled={!streamActive || loading}
            >
                Capture
            </button>

            {loading && <ClipLoader css={override} size={35} color={"#123abc"} loading={loading} />}

            {resultImageUrl && (
                <div className="camera_picture">
                    <img
                        src={resultImageUrl}
                        alt="Captured"
                        style={{ maxWidth: '640px', marginTop: '10px' }}
                    />
                    <button className="bouton_capture" onClick={downloadImage}>
                        Download
                    </button>
                </div>
            )}

            {/* Hidden canvas for capturing frames */}
            <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
    );
}
