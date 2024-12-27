import React from 'react';

interface PaginationProps {
    page: number;
    pageSize: number;
    totalCount: number;
    onPageChange: (newPage: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({ page, pageSize, totalCount, onPageChange }) => {
    const totalPages = Math.ceil(totalCount / pageSize);

    const handlePrevious = () => {
        if (page > 1) {
            onPageChange(page - 1);
        }
    };

    const handleNext = () => {
        if (page < totalPages) {
            onPageChange(page + 1);
        }
    };

    return (
        <div className="flex justify-between items-center mt-4">
            <button onClick={handlePrevious} disabled={page === 1} className="px-4 py-2 bg-gray-200 rounded">
                Previous
            </button>
            <span>
                Page {page} of {totalPages}
            </span>
            <button onClick={handleNext} disabled={page === totalPages} className="px-4 py-2 bg-gray-200 rounded">
                Next
            </button>
        </div>
    );
};

export default Pagination; 