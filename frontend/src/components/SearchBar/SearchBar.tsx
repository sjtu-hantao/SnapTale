import React, { useState } from 'react';
import { Space, Input, DatePicker, Button, Radio, Select, Row, Col } from 'antd';
import dayjs from 'dayjs';
const { RangePicker } = DatePicker;

interface SearchBarProps {
    onFilterChange?: (filters: SearchFilters) => void;
    onFilterSet?: (filters: SearchFilters) => void;
    initFilters?: SearchFilters;
}

interface SearchFilters {
    starred?: boolean;
    device?: string | null;
    fromDate?: string | null;
    toDate?: string | null ;
    contains?: string | null;
}

const dateFormat = 'YYYY-MM-DD';

const SearchBar: React.FC<SearchBarProps> = ({initFilters, onFilterChange, onFilterSet}) => {
    const [contains, setContains] = useState<string>(initFilters?.contains || '');

    const handleStarredChange = (e: any) => { 
        const isChecked = e.target.value === 'starred' ? true : false;
        
        onFilterChange?.({ 
            starred: isChecked, 
            device: initFilters?.device, 
            fromDate: initFilters?.fromDate, 
            toDate: initFilters?.toDate, 
            contains: initFilters?.contains });
    };

    const handleDatePickerChange = (dates: any, dateStrings: [string, string]) => {
        onFilterChange?.({ 
            starred: initFilters?.starred, 
            device: initFilters?.device, 
            fromDate: dateStrings[0], 
            toDate: dateStrings[1], 
            contains: initFilters?.contains });
    };

    const handleDeviceChange = (value: string) => {
        onFilterChange?.({ 
            starred: initFilters?.starred, 
            device: value, 
            fromDate: initFilters?.fromDate, 
            toDate: initFilters?.toDate, 
            contains: initFilters?.contains });
    };

    const handleContainsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setContains(e.target.value);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleFilterButtonClick();
        }
    };

    const handleFilterButtonClick = () => {
        const updatedFilters = { 
            starred: initFilters?.starred, 
            device: initFilters?.device, 
            fromDate: initFilters?.fromDate, 
            toDate: initFilters?.toDate, 
            contains: contains 
          };
          
          onFilterChange?.(updatedFilters);
          
          if (onFilterSet) {
            onFilterSet(updatedFilters);
          }
    }; 
    const fromDateInit = initFilters?.fromDate ? initFilters?.fromDate : "2024-01-01";
    const toDateInit = initFilters?.toDate ? initFilters?.toDate : "2024-12-31";

    return (
        <div style={{width:'80vw'}}>
        <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={6} lg={4}>
                <Radio.Group buttonStyle='solid' onChange={handleStarredChange} value={initFilters?.starred ? 'starred' : 'all'} style={{ width: '100%' }}>
                    <Radio.Button value="all">All</Radio.Button>
                    <Radio.Button value="starred">Starred</Radio.Button>
                </Radio.Group>
            </Col>
            <Col xs={24} sm={12} md={8} lg={6}>
                <RangePicker
                    defaultValue={[dayjs(fromDateInit, dateFormat), dayjs(toDateInit, dateFormat)]}
                    onChange={handleDatePickerChange}
                    style={{ width: '100%' }}
                />
            </Col>
            <Col xs={24} sm={12} md={6} lg={4}>
                <Select 
                    placeholder='Device' 
                    onChange={handleDeviceChange} 
                    value={initFilters?.device} 
                    style={{ width: '100%' }}
                >
                    <Select.Option value="laptop">Laptop</Select.Option>
                    <Select.Option value="tablet">Tablet</Select.Option>
                    <Select.Option value="phone">Phone</Select.Option>
                    <Select.Option value="">All</Select.Option>
                </Select>
            </Col>
            <Col xs={24} sm={12} md={6} lg={6}>
                <Input 
                    placeholder="Search Content..." 
                    onChange={handleContainsChange} 
                    value={contains || ''} 
                    onKeyDown={handleKeyDown} 
                    style={{ width: '100%' }}
                />
            </Col>
            <Col xs={24} sm={24} md={4} lg={4}>
                <Button type="primary" onClick={handleFilterButtonClick} style={{ width: '100%' }}>Filter</Button>
            </Col>
        </Row>
        </div>
    );
};

export default SearchBar;
export type { SearchFilters };
