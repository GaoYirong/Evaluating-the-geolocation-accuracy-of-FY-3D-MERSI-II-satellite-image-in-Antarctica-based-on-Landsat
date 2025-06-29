%% Mann-Kendall Trend Analysis Script (Paired, Compact, Publication Quality - Final Layout v2)
%
%  This script creates highly polished, publication-ready plots with an advanced layout.
%  Key features:
%  1. Uses tiledlayout for a compact arrangement of subplots.
%  2. Subplot titles are placed precisely in the top-left corner OUTSIDE the plot area using text().
%  3. Y-axis labels are dynamically set to 'Displacement (m)' or 'MAD (m)'.
%  4. Legends are placed INSIDE with a transparent background to prevent obscuring data.

% --- Initialization ---
clear;      % Clear workspace variables
clc;        % Clear command window
close all;  % Close all open figure windows

% --- User Configuration ---

% 1. Define the Excel files and corresponding region names
file_list = {
    'Amery_resultstatistics.xlsx', ...
    'AntarcticPeninsula_resultstatistic.xlsx', ...
    'RossIsland_resultstatistics.xlsx', ...
    'QueenMaudLand_resultstatistics.xlsx'
};

region_names = {
    'Amery Ice Shelf', ...
    'Antarctic Peninsula', ...
    'Ross Ice Shelf', ...
    'Queen Maud Land'
};

% 2. Define the "base" variable names to be analyzed in pairs
base_vars_to_analyze = {
    'Bias', ...
    'AbsMean'
};

% 3. Define the column containing the filenames for date extraction
filename_column = 'FileName'; 

% 4. Define subplot labels
subplot_labels = {'(a)', '(b)', '(c)', '(d)'};

% 5. Define significance level (alpha)
alpha = 0.05;

% 6. Image output configuration
save_images = true; 
output_folder = 'Analysis_Plots_Publication_Final'; 
image_format = 'png';
image_resolution = 300;

%% --- Main Processing Loop ---

fprintf('Starting Mann-Kendall trend analysis (Final Layout Mode)...\n');

if save_images
    if ~exist(output_folder, 'dir')
       mkdir(output_folder);
       fprintf('Output folder "%s" created.\n\n', output_folder);
    end
end

% Outer loop: Iterate over each "base" variable pair
for j = 1:length(base_vars_to_analyze)
    base_var_name = base_vars_to_analyze{j};
    
    along_var_name = ['Along_' base_var_name];
    cross_var_name = ['Cross_' base_var_name];
    
    fprintf('--- Processing variable pair: %s and %s ---\n', along_var_name, cross_var_name);

    figure('Position', [100, 100, 2000, 1500]); 
    
    t = tiledlayout(2, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

    % Inner loop: Iterate over each file (region)
    for i = 1:length(file_list)
        filename = file_list{i};
        region = region_names{i};

        ax = nexttile;
        hold(ax, 'on');
        
        % --- Data Loading and Pre-processing ---
        try
            if ~isfile(filename)
                error('File not found: %s', filename);
            end
            T = readtable(filename);
            
            if ~ismember(filename_column, T.Properties.VariableNames)
                error('Filename column "%s" not found.', filename_column);
            end
            fname_parts = split(T.(filename_column), '_');
            date_strings = fname_parts(:, 1);
            date_array = datetime(date_strings, 'InputFormat', 'yyyyMMdd');
            T.Date = date_array;
            
            month_filter = ismember(month(T.Date), [1, 2, 11, 12]);
            T_filtered = T(month_filter, :);
            
            if isempty(T_filtered)
                error('No data for specified months.');
            end

            year_vector = year(T_filtered.Date);
            [counts, years] = groupcounts(year_vector);
            
            x_positions = zeros(height(T_filtered), 1);
            xticks_positions = [];
            xticklabels_cell = {};
            current_pos = 1;
            for k = 1:length(years)
                year_k = years(k);
                count_k = counts(k);
                indices_in_year = find(year_vector == year_k);
                x_positions(indices_in_year) = current_pos : (current_pos + count_k - 1);
                xticks_positions = [xticks_positions, current_pos + (count_k - 1) / 2];
                xticklabels_cell = [xticklabels_cell, num2str(year_k)];
                current_pos = current_pos + count_k;
            end
        catch data_err
            warning('Data processing error for %s: %s', filename, data_err.message);
            title_text = sprintf('%s %s (Data Error)', subplot_labels{i}, region);
            text(ax, 0, 1.02, title_text, 'Units', 'normalized', 'VerticalAlignment', 'bottom', ...
                 'HorizontalAlignment', 'left', 'FontSize', 26, 'FontWeight', 'bold');
            box(ax, 'on'); set(ax, 'xtick', [], 'ytick', []);
            hold(ax, 'off'); continue;
        end
        
        % --- Data Extraction and Plotting ---
        legend_items = []; 
        legend_texts = {}; 
        
        if ismember(along_var_name, T_filtered.Properties.VariableNames)
            along_data = T_filtered.(along_var_name);
            valid_idx = ~isnan(along_data);
            [h_a, p_a] = mann_kendall(along_data(valid_idx), alpha);
            p1 = plot(ax, x_positions(valid_idx), along_data(valid_idx), 's', 'MarkerEdgeColor', 'k', 'MarkerFaceColor', [0.3 0.6 1], 'MarkerSize', 10);
            coeffs_a = polyfit(x_positions(valid_idx), along_data(valid_idx), 1);
            trend_a = polyval(coeffs_a, x_positions(valid_idx));
            plot(ax, x_positions(valid_idx), trend_a, '-', 'Color', [0 0 0.8], 'LineWidth', 3);
            
            fprintf('    Along-track -> h: %d, p: %.4f\n', h_a, p_a);
            legend_items = [legend_items, p1];
            sig_text_a = 'not significant'; if h_a == 1, sig_text_a = 'significant'; end
            legend_texts = [legend_texts, {sprintf('Along-track (p=%.3f, %s)', p_a, sig_text_a)}];
        end

        if ismember(cross_var_name, T_filtered.Properties.VariableNames)
            cross_data = T_filtered.(cross_var_name);
            valid_idx = ~isnan(cross_data);
            [h_c, p_c] = mann_kendall(cross_data(valid_idx), alpha);
            p3 = plot(ax, x_positions(valid_idx), cross_data(valid_idx), 'o', 'MarkerEdgeColor', 'k', 'MarkerFaceColor', [1 0.6 0.6], 'MarkerSize', 10);
            coeffs_c = polyfit(x_positions(valid_idx), cross_data(valid_idx), 1);
            trend_c = polyval(coeffs_c, x_positions(valid_idx));
            plot(ax, x_positions(valid_idx), trend_c, '-', 'Color', [0.8 0 0], 'LineWidth', 3);
            
            fprintf('    Cross-track -> h: %d, p: %.4f\n', h_c, p_c);
            legend_items = [legend_items, p3];
            sig_text_c = 'not significant'; if h_c == 1, sig_text_c = 'significant'; end
            legend_texts = [legend_texts, {sprintf('Cross-track (p=%.3f, %s)', p_c, sig_text_c)}];
        end
        
        % --- Finalize Subplot ---
        hold(ax, 'off');
        grid(ax, 'on');
        box(ax, 'on');
        
        % *** MODIFICATION 1: Place title precisely in top-left OUTSIDE the axes ***
        title_text = sprintf('%s %s', subplot_labels{i}, region);
        text(ax, 0, 1.02, title_text, 'Units', 'normalized', 'VerticalAlignment', 'bottom', ...
             'HorizontalAlignment', 'left', 'FontSize', 26, 'FontWeight', 'bold');
        
        ax.FontSize = 24; 
        
        ax.XTick = xticks_positions;
        ax.XTickLabel = xticklabels_cell;
        ax.XTickLabelRotation = 0; 
        
        if ~isempty(legend_items)
            legend(ax, legend_items, legend_texts, 'Location', 'northeast', 'FontSize', 24, 'Box', 'off');
        end

    end % End of inner loop (regions)
    
    % *** MODIFICATION 2: Dynamically set the Y-axis label for the whole layout ***
    if strcmp(base_var_name, 'Bias')
        y_label_text = 'Displacement (m)';
    elseif strcmp(base_var_name, 'AbsMean')
        y_label_text = 'MAD (m)';
    else
        % Fallback for any other variable names
        y_label_text = sprintf('%s (m)', strrep(base_var_name, '_', ' '));
    end
    
    xlabel(t, 'Year', 'FontSize', 28, 'FontWeight', 'bold');
    ylabel(t, y_label_text, 'FontSize', 28, 'FontWeight', 'bold');

    % --- Save the entire figure ---
    if save_images
        image_filename = sprintf('Analysis_Group_FinalLayout_%s.%s', base_var_name, image_format);
        full_path = fullfile(output_folder, image_filename);
        
        print_format = ['-d' image_format];
        print_resolution = ['-r' num2str(image_resolution)];
        print(gcf, full_path, print_format, print_resolution);
        
        fprintf('  Group plot saved to: %s\n\n', full_path);
    else
        fprintf('\n');
    end

end % End of outer loop (variable pairs)

fprintf('--- All analyses complete ---\n');